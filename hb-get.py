#!/bin/python
import sys
from os import path, makedirs
from requests import get
from bs4 import BeautifulSoup

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python hb-get.py <HumbleBundle.html> <output directory> [filetype]")
        print("Filetype defaults to PDF and is optional.")
    else:
        OUTPUT_DIR = path.abspath(sys.argv[2])
        with open(sys.argv[1]) as f:
            soup = BeautifulSoup(f, "html.parser")

        dl_links = soup.select(".download a[href^='https://dl.humble.com']")
        
        # Filter links by file type 
        filetype = "PDF" if len(sys.argv) < 5 else sys.argv[4]
        dl_links = list(filter(lambda x: x.get_text().strip() == filetype, dl_links))

        failed_dl_count = 0
        for link in dl_links:
            btn_text = link.get_text().strip()
            url = str(link['href'])
            filename = url.split("?")[0][22:]
            
            filepath = path.join(OUTPUT_DIR, filename)
            if path.exists(filepath):
                print(f"Skipping... {filepath} already exists")
                continue
            else:
                print(f"Downloading {filename} ... ", end="", flush=True)

            # TODO: add progress bar per file
            # Fetch file from web
            file = get(url)
            if file.status_code < 200 or file.status_code > 299:
                print(f"Failed to download {filename}. Status code: {file.status_code}", end="")
                failed_dl_count += 1
                continue

            # Create output directory
            try:
                makedirs(OUTPUT_DIR)
            except OSError as e:
                pass # ignore error if OUTPUT_DIR already exists
                
            # Write to file
            try:
                with open(filepath, "w+b") as f:
                    f.write(file.content)

                print("Done")
            except (OSError, IOError) as e:
                print(f"Could not open {filepath}")
                print(e)


        print("\nDownloads complete:")
        print(f"\t{failed_dl_count} failed downloads")
