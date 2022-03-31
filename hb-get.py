#!/bin/python
import sys
from requests import get
from bs4 import BeautifulSoup
from tqdm import tqdm

if __name__ == "__main__":
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Usage: python hb-get.py <HumbleBundle.html> <output directory> [filetype]")
        print("Filetype defaults to PDF and is optional.")
    else:
        with open(sys.argv[1]) as f:
            soup = BeautifulSoup(f, "html.parser")

        dl_links = soup.select(".download a[href^='https://dl.humble.com']")
        
        # Filter links by file type 
        filetype = "PDF" if len(sys.argv) < 4 else sys.argv[3]
        dl_links = list(filter(lambda x: x.get_text().strip() == filetype, dl_links))

        failed_dl_count = 0
        # progress = tqdm(dl_links)
        for link in dl_links:
            btn_text = link.get_text().strip()
            url = str(link['href'])
            filename = url.split("?")[0][22:]
            
            # progress.set_description(f"Downloading {filename}")
            # TODO: add progress bar per file
            print(f"Downloading {filename} ... ", end="", flush=True)

            # Fetch file from web
            file = get(url)
            if file.status_code < 200 or file.status_code > 299:
                print(f"Failed to download {filename}. Status code: {file.status_code}", end="")
                failed_dl_count += 1
                continue

            # Write to file
            with open(filename, "w+b") as f:
                f.write(file.content)

            print("Done")

        print("\nDownloads complete:")
        print(f"\t{failed_dl_count} failed downloads")
