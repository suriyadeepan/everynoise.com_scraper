RES_URL= 'http://everynoise.com'

import requests
import os
import argparse

from bs4 import BeautifulSoup
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument("--out", default='./', 
        help='[./] Folder to store downloaded content')
parser.add_argument("--cache_links", action='store_true', default=True, 
        help='[True] Saves download links to a file')
args = parser.parse_args()


def parse_resource_content(url=RES_URL):
    """
    o Download contents of Source URL http://everynoise.com
    o Parse with Beautiful Soup
    o Extract div's of class "genre scanme"

    Args:
        url (str): [http://everynoise.com] source url

    Returns:
        list: div elements of class "genre scanme"
    """
    soup = BeautifulSoup(requests.get(url).text, 'lxml')
    # parse rule
    return soup.find_all('div', attrs={ "class" : "genre scanme" })

def download_through_requests(url, filename, timeout=10):
    """
    Use requests module to download mp3 file, chunk by chunk
     
    Args:
        url      (str): url to download mp3 file
        filename (str): name to save file
        timeout  (int): [10] #seconds to wait to throw TimedOut exception
    """
    try:
        request = requests.get(url, timeout=timeout, stream=True)
        with open(filename, 'wb') as f:
            for chunk in request.iter_content(1024*1024):
                f.write(chunk)
    except:
        print('Request timed out for "{}" !!'.format(url))

def fetch_downloadable_files():
    """
    Fetch mp3 file information as list from everynoise.com

    Returns:
        list: samples [ { 'url' : .. , 'name' : .. , 'filename' : .. } .. ]
    """
    samples = []
    for div in parse_resource_content():
        url = div.attrs.get('preview_url')
        title = div.text[:-2]
        if url and title:
            samples.append( {
                'url'  : url,
                'name' : title,
                'filename' : (title + '.mp3').replace(' ', '_')
                })

    return samples

def create_dir(path):
    # create directory if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path)

def write_links_to_file(samples, path):
    """
    Write samples to file (url, name, filename)
     Attributes separated by a delimiter 

     name||filename||url

    Args:
        samples (list): list of samples
    """
    with open(os.path.join(path, 'mp3-links.list'), 'w') as f:
        for sample in samples:
            f.write('{}||{}||{}\n'.format(
                sample['name'], # ||
                sample['filename'], # ||
                sample['url']))


if __name__ == '__main__':
    # fetch downloadable links
    samples = fetch_downloadable_files()

    # create output directory if necessary
    create_dir(args.out)

    # cache links
    if args.cache_links:
        write_links_to_file(samples, args.out)

    # download files
    for sample in tqdm(samples):
        download_through_requests(sample['url'], 
                os.path.join(args.out, sample['filename'])
                )
