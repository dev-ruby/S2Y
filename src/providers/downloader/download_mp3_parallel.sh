#!/bin/bash

INPUT_FILE=$1

sanitize_filename() {
    echo "$1" | sed 's/[\\/*?:"<>|]//g' | sed 's/ *$//'
}

download_mp3() {
    IFS="|" read -r url filename dir <<< "$1"
    safe_title=$(sanitize_filename "$filename")
    mkdir -p "./tmp/${dir}"
    # yt-dlp -x --audio-format mp3 -o "./tmp/${dir}/${safe_title}.%(ext)s" "$url"
    yt-dlp -f bestaudio -o - "$url" | ffmpeg -threads 1 -i pipe:0 -vn -acodec libmp3lame -ab 192k "./tmp/${dir}/${safe_title}.mp3" && echo "Completed $filename"
}

export -f sanitize_filename
export -f download_mp3

parallel --ungroup -j$(($(nproc) - 1)) download_mp3 :::: "$INPUT_FILE"
