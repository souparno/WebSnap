import argparse
import logging
from downloader import download_site

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Clone a website to a local directory.")
    parser.add_argument("url", help="The URL of the site to clone")
    parser.add_argument("local_directory", help="The local directory to clone the site into")
    
    args = parser.parse_args()
    
    site_url = args.url
    local_directory = args.local_directory
    
    download_site(site_url, local_directory)
