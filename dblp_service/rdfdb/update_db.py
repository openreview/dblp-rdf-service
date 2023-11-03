import requests
from tqdm import tqdm
import hashlib

# https://dblp.org/rdf/
## default to latest..
# /rdf
#  STATISTICS.txt 2023-11-03 19:02 199
#  dblp.ttl.gz 2023-11-03 19:05 1.6G
#  dblp.ttl.gz.md5 2023-11-03 19:05 46
#  release/ 2023-11-03 17:58 -
#  schema 2023-03-17 13:18 41K
#  schema-2020-07-01 2023-03-17 13:18 28K
#  schema-2021-09-11 2023-03-17 13:18 35K
#  schema-2022-03-02 2023-03-17 13:18 36K
#  schema-2022-09-09 2023-03-17 13:18 41K
#  schema.nt 2023-03-17 13:18 80K
#  schema.ttl 2023-03-17 13:18 26K

# content of /rdf/release
# dblp-2023-10-01.nt.gz.md5
# dblp-2023-10-01.nt.gz
# dblp-2023-09-01.nt.gz.md5
# dblp-2023-09-01.nt.gz



# write a python function that downloads the files
# https://dblp.org/rdf/dblp.ttl.gz and https://dblp.org/rdf/dblp.ttl.gz.md5. The
# function should show overall progress of the downloads. The files should be
# saved to disk, then the integrity of the downloaded dblp.ttl.gz file should be
# verified using the dblp.ttl.gz.md5 hash file.

def download_file(url: str, filename: str):
    # Stream the download to handle large files
    response = requests.get(url, stream=True)
    total_size_in_bytes = int(response.headers.get('content-length', 0))
    block_size = 1024  # 1 Kibibyte
    progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)
    with open(filename, 'wb') as file:
        for data in response.iter_content(block_size):
            progress_bar.update(len(data))
            file.write(data)
    progress_bar.close()
    if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
        print("ERROR, something went wrong")
    return filename

def verify_md5(filename: str, md5_hash: str):
    md5 = hashlib.md5()
    with open(filename, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b""):
            md5.update(chunk)
    file_md5_hash = md5.hexdigest()
    return file_md5_hash == md5_hash

def download_and_verify_dblp_ttl():
    # URLs for the files
    file_url = 'https://dblp.org/rdf/dblp.ttl.gz'
    md5_url = 'https://dblp.org/rdf/dblp.ttl.gz.md5'

    # Download the files
    print("Downloading the .ttl.gz file...")
    ttl_gz_filename = download_file(file_url, 'dblp.ttl.gz')
    print("Downloading the .md5 file...")
    md5_filename = download_file(md5_url, 'dblp.ttl.gz.md5')

    # Read the MD5 hash from the downloaded .md5 file
    with open(md5_filename, 'r') as file:
        md5_hash = file.read().split()[0]

    # Verify the integrity of the .ttl.gz file
    print("Verifying the integrity of the .ttl.gz file...")
    if verify_md5(ttl_gz_filename, md5_hash):
        print("Integrity check passed.")
    else:
        print("Integrity check failed!")
