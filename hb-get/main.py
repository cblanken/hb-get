#!/bin/python
import argparse
from concurrent.futures import ThreadPoolExecutor
import os
from functools import partial
from pathlib import Path
from pprint import pprint
import requests
import signal
from threading import Event
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchWindowException, TimeoutException
import selenium_driver as sd

from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

parser = argparse.ArgumentParser(
        prog="hb-get",
        description="Humble Book Bundle download program",
        epilog="")

parser.add_argument("-o", "--output_dir", nargs="?", default="./downloads",
                    help="Output directory")
parser.add_argument("--html", action="store_true",
                    help="Read from HTML input file instead of scraping humblebundle.com")
parser.add_argument("-f", "--filetype", nargs="?", default="pdf",
                    help="Filetype of file to extract from bundle. Note files without a \
                        corresponding version in the [filetype] format will not be downloaded.")

args = parser.parse_args()

class Downloader:
    def __init__(self):
        self.progress = Progress(
            TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
            BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "⋅",
            DownloadColumn(),
            "⋅",
            TransferSpeedColumn(),
            "⋅",
            TimeRemainingColumn(),
        )

        self.done_event: Event = Event()
        signal.signal(signal.SIGINT, self.handle_sigint)


    def handle_sigint(self, _signum, _frame):
        self.done_event.set()

    def save_from_url(self, task_id: TaskID, url: str, output_dir: Path, filename: str):
        filepath = Path(output_dir, filename)
        if filepath.exists():
            self.progress.console.log(f"Skipping {filepath}, already exists")
            return

        # Fetch file from web
        response = requests.get(url, stream=True, timeout=5)

        # Write to file
        try:
            with open(filepath, "wb") as file:
                self.progress.start_task(task_id)
                for data in response.iter_content(chunk_size=32768):
                    file.write(data)
                    self.progress.update(task_id, advance=len(data))
                    if self.done_event.is_set():
                        return
            self.progress.console.log(f"Downloaded {filename}")

        except (OSError, IOError) as exc:
            self.progress.console.log(f"Could not open {filename}, skipping")
            self.progress.console.log(exc)

    def download(self, urls_by_title: dict[str, str], output_dir: Path):
        """Download files from a list of urls
        """
        with self.progress:
            with ThreadPoolExecutor(max_workers=8) as pool:
                for title, url in urls_by_title.items():
                    task_id = self.progress.add_task("download", filename=title, start=False)
                    pool.submit(self.save_from_url, task_id, url, output_dir, title)


def main():
    if args.html:
        with open(args.html, encoding="utf-8") as fp:
            soup = BeautifulSoup(fp, "html.parser")

        dl_hrefs = soup.select(".download a[href^='https://dl.humble.com']")

        # Filter links by file type
        filtered_hrefs = list(
            filter(lambda x: x.get_text().strip().lower() == args.filetype, dl_hrefs))

        for i, link in enumerate(filtered_hrefs):
            pprint(i, link)
    else:
        try:
            hb = sd.HumbleDriver("https://www.humblebundle.com")
            hb.login()

            print("> Retrieving purchases...")
            purchases_titles = hb.get_purchases()
            purchase = hb.select_purchase()

            print("> Retrieving download links...")
            download_links_by_title = hb.get_download_links_by_filename(args.filetype)

            # Create output directory
            output_dir = Path(args.output_dir, purchase)
            output_dir.mkdir(parents=True, exist_ok=True)

            downloader = Downloader()
            downloader.download(download_links_by_title, output_dir)
        except KeyboardInterrupt:
            print("\nKeyboard Interrupt: stopping...")
        except (NoSuchWindowException, TimeoutException) as exc:
            print("The browser session ended or timed out. Exiting...")

if __name__ == "__main__":
    main()
