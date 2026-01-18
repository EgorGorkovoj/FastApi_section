import asyncio
import datetime
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import pandas as pd
from .parser import BulletinLinkExtractor

import aiohttp
from aiolimiter import AsyncLimiter
from .collector import BulletinCollector
from core.config import DOWNLOADS_DIR, url
from core.db_depends import AsyncSessionLocal
from core.http.cookies import create_cookie_jar
from core.http.headers import HEADERS
from core.logger import logger
from .file_loader import AcyncioXMLFileDownloader
from .page_load import RequestPageLoader
from .parser_services.excel_worker import ExcelParseWorker
from .parser_services.importer_db import SpimexImporterDB


class SpimexParserRun:
    """
    Оркестратор асинхронного парсинга биржевых бюллетеней SPIMEX.

    Отвечает за полный цикл обработки данных:
        1. Сбор ссылок на бюллетени за период
        2. Асинхронную загрузку файлов
        3. Парсинг Excel-файлов в DataFrame (в отдельных процессах)
        4. Сохранение данных в базу данных

    Поддерживает ограничение конкурентности:
        - по количеству одновременно загружаемых страниц
        - по количеству одновременно скачиваемых файлов

    Используется как единая точка входа для запуска парсинга.
    """

    def __init__(
        self,
        start_date: datetime.date,
        end_date: datetime.date,
        max_concurrent_pages: int = 7,
        max_concurrent_files: int = 7,
    ):
        """
        Инициализация параметров парсинга.

        Args:
            start_date (datetime.date): Начальная дата периода парсинга.
            end_date (datetime.date): Конечная дата периода парсинга.
            max_concurrent_pages (int): Максимальное количество
                одновременно загружаемых HTML-страниц.
            max_concurrent_files (int): Максимальное количество
                одновременно загружаемых файлов.
        """

        self.start_date = start_date
        self.end_date = end_date

        self.page_semaphore = asyncio.Semaphore(max_concurrent_pages)
        self.file_limiter = AsyncLimiter(max_concurrent_files, 1)

    async def collect_links(self, http_session) -> list[tuple[str, datetime.date]]:
        """
        Собирает ссылки на бюллетени за указанный период.

        Использует асинхронную загрузку страниц с ограничением
        по количеству одновременных запросов.

        Args:
            http_session: Активная aiohttp-сессия.

        Returns:
            list[tuple[str, datetime.date]]:
                Список кортежей (url файла, дата торгов).
        """

        response = RequestPageLoader(session=http_session)
        extractor = BulletinLinkExtractor(url.SITE_URL)
        collector = BulletinCollector(
            url.PAGE_URL, response, extractor, self.start_date, self.end_date
        )
        links = await collector.collect(semaphore=self.page_semaphore)
        logger.info(f'Количество ссылок: {len(links)}')
        return links

    async def download_files(
        self,
        http_session,
        links: list[tuple[str, datetime.date]],
    ) -> list[tuple[Path | None, datetime.date]]:
        """
        Асинхронно загружает файлы бюллетеней по полученным ссылкам.

        Загрузка выполняется параллельно с ограничением
        количества активных задач.

        Args:
            http_session: Активная aiohttp-сессия.
            links (list[tuple[str, datetime.date]]):
                Список ссылок на файлы и соответствующих дат.

        Returns:
            list[tuple[Path | None, datetime.date]]:
                Пути к загруженным файлам и даты торгов.
                В случае ошибки путь может быть None.
        """

        response = RequestPageLoader(session=http_session)
        downloader = AcyncioXMLFileDownloader(
            DOWNLOADS_DIR,
            response,
            self.file_limiter,
        )

        downloaded_files = []

        try:
            async with asyncio.TaskGroup() as tg:
                tasks = {
                    tg.create_task(
                        downloader.download(
                            link,
                            link.split('reports/oil_xls/')[-1],
                        )
                    ): date
                    for link, date in links
                }

            for task, date in tasks.items():
                file_path = task.result()
                downloaded_files.append((file_path, date))

        except* Exception as e:
            for error in e.exceptions:
                logger.warning(f'Ошибка загрузки файла: {error}')

        logger.info(f'Количество загруженных файлов: {len(downloaded_files)}')
        return downloaded_files

    def parse_excels(
        self,
        downloaded_files: list[tuple[Path | None, datetime.date]],
    ) -> list[tuple[pd.DataFrame, datetime.date]]:
        """
        Парсит Excel-файлы в pandas DataFrame.

        Парсинг выполняется в отдельных процессах
        для обхода GIL и ускорения CPU-bound операций.

        Args:
            downloaded_files (list[tuple[Path | None, datetime.date]]):
                Пути к файлам и соответствующие даты.

        Returns:
            list[tuple[pd.DataFrame, datetime.date]]:
                Список DataFrame с привязкой к дате торгов.
        """

        df_list = []

        try:
            with ProcessPoolExecutor(max_workers=os.cpu_count()) as pool:
                for df, file_date in pool.map(
                    ExcelParseWorker.parse,
                    downloaded_files,
                ):
                    df_list.append((df, file_date))

        except Exception as e:
            logger.warning(f'Ошибка парсинга Excel: {e}')

        return df_list

    async def save_to_db(
        self,
        df_list: list[tuple[pd.DataFrame, datetime.date]],
    ) -> None:
        """
        Сохраняет распарсенные данные в базу данных.

        Использует bulk-вставку для повышения производительности.

        Args:
            df_list (list[tuple[pd.DataFrame, datetime.date]]):
                Список датафреймов с датами торгов.
        """

        try:
            async with AsyncSessionLocal() as session:
                importer = SpimexImporterDB(session)
                await importer.save_table_bulk(df_list)
        except Exception as e:
            logger.warning(f'Ошибка сохранения в БД: {e}')

    async def run(self) -> None:
        """
        Запускает полный цикл парсинга.

        Последовательно выполняет:
            - сбор ссылок
            - загрузку файлов
            - парсинг Excel
            - сохранение в БД
        """

        async with aiohttp.ClientSession(
            headers=HEADERS,
            cookie_jar=create_cookie_jar(),
        ) as http_session:

            links = await self.collect_links(http_session)
            downloaded_files = await self.download_files(http_session, links)

        df_list = self.parse_excels(downloaded_files)
        await self.save_to_db(df_list)
