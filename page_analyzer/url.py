import requests

from urllib.parse import urlparse
from validators.url import url as validate_url
from validators import ValidationError
from bs4 import BeautifulSoup


def normalize_url(url):
    parsed_url = urlparse(url)
    return parsed_url._replace(
        path='', params='', query='', fragment='').geturl()


def is_url_correct(url):
    return not isinstance(validate_url(url), ValidationError)


def parse_url(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    description_tag = soup.find(
        'meta',
        attrs={'name': 'description'}
    )
    return {
        "description": description_tag['content'] if description_tag else None,
        "title": soup.title.string if soup.title else None,
        "h1": soup.h1.string if soup.h1 else None,
        "status_code": response.status_code
    }
