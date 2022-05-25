# hb-get

## Usage
1. Save the HTML of the Humble Bundle purchase page for the bundle you want to download. In the example below this is the `hb.html` file. 
2. Execute the script with arguments for the HTML file, output directory and filetype respectively
```console
$ python hb-get.py
Usage: python hb-get.py <hb.html> <output directory> [filetype]
Filetype defaults to PDF and is optional.
```
Some other formats that might be available are `epub` and `mobi`. Just note that if you specify a format, the script will only download a book if it's available in the given format. PDF is the default since most books in Humble Bundles provide a PDF.

[![asciicast](https://asciinema.org/a/Ysb8wgqcCbEV1tKal58StElEd.svg)](https://asciinema.org/a/Ysb8wgqcCbEV1tKal58StElEd?autoplay=1)
