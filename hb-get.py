#!/bin/python
import argparse
import os
import pathlib
import sys
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import selenium_driver as sd


parser = argparse.ArgumentParser(
        prog="hb-get",
        description="Humble Book Bundle download script",
        epilog="")

parser.add_argument("-o", "--output_dir", nargs="?", help="Output directory")
parser.add_argument("-i", "--html", nargs="?", help="Input bundle HTML file")
parser.add_argument("-f", "--filetype", nargs="?", default="pdf", help="Filetype of file to extract from bundle.\
                    Note files without a corresponding version in the [filetype] format will not be downloaded.")
parser.add_argument("-m", "--mfa", action="store_true", help="Check for MFA (Multi-Factor Auth)")

args = parser.parse_args()

def save_from_url(url: str, output_dir: str, filename: str):
    filepath = pathlib.Path(output_dir, filename)
    if os.path.exists(filepath):
        print(f"Skipping... {filepath} already exists")
        return
    else:
        print(f"Downloading {filename} ... ", end="", flush=True)

    # TODO: add progress bar per file
    # Fetch file from web
    file = requests.get(url)
    if file.status_code != requests.status_codes.codes.ok:
        print(f"Failed to download {filename}. Status code: {file.status_code}", end="", flush=True)
        return

    # Create output directory
    try:
        os.makedirs(output_dir)
    except OSError as e:
        pass # ignore error if output_dir already exists
        
    # Write to file
    try:
        with open(filepath, "w+b") as fp:
            fp.write(file.content)

        print("Done")
    except (OSError, IOError) as e:
        print(f"Could not open {filepath}")
        print(e)

if __name__ == "__main__":
    if args.html:
        with open(args.html) as fp:
            soup = BeautifulSoup(fp, "html.parser")

        dl_hrefs = soup.select(".download a[href^='https://dl.humble.com']")
        
        # Filter links by file type 
        filtered_hrefs = list(filter(lambda x: x.get_text().strip().lower() == args.filetype, dl_hrefs))

        for i, link in enumerate(filtered_hrefs):
            pprint(link)
            breakpoint()
            btn_text = link.get_text().strip()
            url = str(link['href'])
            filename = url.split("?")[0][22:]
            if args.output_dir:
                save_from_url(url, args.output_dir, filename)

    else:
        hb = sd.HumbleDriver("https://www.humblebundle.com")
        hb.login()
        purchases = hb.get_purchases()
        hb.select_purchase()
        download_links_by_title = hb.get_download_links_by_title(args.filetype)
        for title, url in download_links_by_title.items():
            if args.output_dir:
                save_from_url(url, args.output_dir, f"{title}.{args.filetype}")
            else:
                print(f"{title}: {url})")

