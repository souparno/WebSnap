# Website Cloner

This project is a Python script to download a website to a local directory. It utilizes Tor for anonymous browsing and focuses on downloading specific file types and updating local links. 

## Features

- Downloads various file types including `.svg`, `.jpg`, `.jpeg`, `.png`, `.gif`, `.ico`, `.css`, `.js`, `.html`, `.php`, `.json`, `.ttf`, `.otf`, `.woff2`, `.woff`, `.eot`, `.mp4`, and `.ogg`.
- Scans specific file types for additional links to download.
- Uses Tor for anonymous browsing.
- Maintains a global URL map to correctly resolve relative paths in downloaded files.

## Requirements

- Python 3.x
- `requests` library
- `tor` (Tor must be running on your machine)
- `socks5h` proxy

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/website-cloner.git
    cd website-cloner
    ```

2. Install the required Python libraries:
    ```sh
    pip install requests
    ```

3. Ensure that Tor is running on your machine:
    ```sh
    tor
    ```

## Usage

To clone a website to a local directory, run:

```sh
python main.py <URL> <LOCAL_DIRECTORY>
