#!/bin/python
import argparse
import os
import pathlib
import sys
import requests
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(
        prog="hb-get",
        description="Humble Book Bundle download script",
        epilog="")

parser.add_argument("-o", "--output_dir", nargs="?", default=pathlib.Path("./output/"), help="Output directory")
parser.add_argument("-i", "--html", nargs="?", help="Input bundle HTML file")
parser.add_argument("-f", "--filetype", nargs="?", default="pdf", help="Filetype of file to extract from bundle.\
                    Note files without a corresponding version in the [filetype] format will not be downloaded.")

args = parser.parse_args()

if __name__ == "__main__":
    if args.html:
        OUTPUT_DIR = os.path.abspath(args.output_dir)
        with open(args.html) as fp:
            soup = BeautifulSoup(fp, "html.parser")

        dl_links = soup.select(".download a[href^='https://dl.humble.com']")
        
        # Filter links by file type 
        dl_links = list(filter(lambda x: x.get_text().strip() == args.filetype, dl_links))

        failed_dl_count = 0
        breakpoint()
        for link in dl_links:
            btn_text = link.get_text().strip()
            url = str(link['href'])
            filename = url.split("?")[0][22:]
            
            filepath = os.path.join(OUTPUT_DIR, filename)
            if os.path.exists(filepath):
                print(f"Skipping... {filepath} already exists")
                continue
            else:
                print(f"Downloading {filename} ... ", end="", flush=True)

            # TODO: add progress bar per file
            # Fetch file from web
            file = requests.get(url)
            if file.status_code < 200 or file.status_code > 299:
                print(f"Failed to download {filename}. Status code: {file.status_code}", end="")
                failed_dl_count += 1
                continue

            # Create output directory
            try:
                os.makedirs(OUTPUT_DIR)
            except OSError as e:
                pass # ignore error if OUTPUT_DIR already exists
                
            # Write to file
            try:
                with open(filepath, "w+b") as fp:
                    fp.write(file.content)

                print("Done")
            except (OSError, IOError) as e:
                print(f"Could not open {filepath}")
                print(e)


        print("\nDownloads complete:")
        print(f"\t{failed_dl_count} failed downloads")

    else:
        print("hi")
