"""Download latest rdf db files from https://dblp.org .

Retrieves *.rdf + *.mdf, downloads and verifies file

"""

import requests
from tqdm import tqdm
import hashlib


def download_file(url: str, filename: str):
    # Stream the download to handle large files
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get("content-length", 0))
    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit="iB", unit_scale=True)
    with open(filename, "wb") as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")
    return filename


def fetch_file_content(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()  # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    return str(response.content, "utf-8")


def verify_md5(filename: str, md5_hash: str):
    md5 = hashlib.md5()
    with open(filename, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            md5.update(chunk)
    file_md5_hash = md5.hexdigest()
    return file_md5_hash == md5_hash


def download_and_verify_dblp_ttl():
    # URLs for the files
    file_url = "https://dblp.org/rdf/dblp.ttl.gz"
    md5_url = "https://dblp.org/rdf/dblp.ttl.gz.md5"

    # Download the files
    print("Downloading the .ttl.gz file...")
    ttl_gz_filename = download_file(file_url, "dblp.ttl.gz")
    print("Downloading the .md5 file...")
    md5_filename = download_file(md5_url, "dblp.ttl.gz.md5")

    # Read the MD5 hash from the downloaded .md5 file
    with open(md5_filename, "r") as file:
        md5_hash = file.read().split()[0]

    # Verify the integrity of the .ttl.gz file
    print("Verifying the integrity of the .ttl.gz file...")
    if verify_md5(ttl_gz_filename, md5_hash):
        print("Integrity check passed.")
    else:
        print("Integrity check failed!")
