# hb-get - Humble Bundle purchase downloader
`hb-get` is a command line tool for downloading files available in [Humble Bundles](https://www.humblebundle.com/)

I buy a lot of Humble (Book) Bundles. Unfortunately, as the time of this writing, the only way to download all the books in a recent purchase is to click the _BULK DOWNLOAD_ button and manually accept all the download prompts from the browser. I was sick of doing this everytime I purchased a new bundle and thought this would be a fun excuse to experiment with [Selenium](https://www.selenium.dev/documentation).

# Install
Install [Poetry](https://python-poetry.org/docs/#installation) for virtual environment setup and installing the dependencies
```shell
# Download repo
git clone https://github.com/cblanken/hb-get.git
cd ./hb-get

# Install dependencies
poetry install

# Run downloader
poetry run main

# Alternatively run with
python ./hb-get/main.py
```

# Usage
```
usage: hb-get [-h] [-o [OUTPUT_DIR]] [-f [FILETYPE]] [-t [TITLE_INCLUDES]]

Humble Book Bundle download program. Use the HBGET_USER and HBGET_PASS environment variables to
specify username and password for login. Otherwise you will be prompted during the login process

options:
  -h, --help            show this help message and exit
  -o [OUTPUT_DIR], --output_dir [OUTPUT_DIR]
                        Output directory
  -f [FILETYPE], --filetype [FILETYPE]
                        Filetype of file to extract from bundle. Note files without a corresponding version in the [filetype]
                        format will not be downloaded.
  -t [TITLE_INCLUDES], --title-includes [TITLE_INCLUDES]
                        Filters purchases by title.
```

## Demo
Below is a short demo of installing the tool and using it to download books from a bundle.

![demo-gif](https://github.com/cblanken/hb-get/assets/19908880/e657d364-8bac-4646-9222-363c0f9e7b40)

- The demo above has already specified a username and password via the environment variables `HBGET_USER` and `HBGET_PASS`. If these aren't provided then the program will request them before initiating the login process
- The `-t` flag used with `poetry run main` specifies a filter for purchases by their titles. As seen in the demo, only purchases with "Book Bundle" in their title are shown with an option to download.
- The default format for download is `pdf` though that can be changed with the `-f` flag

# Credits
This software uses the following open source packages
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/#)
- [requests](https://requests.readthedocs.io/en/latest/)
- [rich](https://github.com/Textualize/rich) 
- [Selenium](https://www.selenium.dev/documentation)

# License
This project is licensed under the MIT license - see [LICENSE.md](./LICENSE.md) for details
