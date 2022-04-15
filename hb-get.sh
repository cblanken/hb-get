#!/bin/bash

# A script to download HumbleBundle PDFs or other files from provided links.txt
output_dir="$PWD"
download_hb_file () {
    url="$1"
    filename=$(echo "$url" | cut -d'?' -f1 | cut -d'/' -f4)
    wget --no-verbose -O "$output_dir/$filename" "$url"
}

while read -r line; do
    link="$line"
    download_hb_file "$link"
done < "$1"
