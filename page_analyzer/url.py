from urllib.parse import urlparse
from validators.url import url as validate_url
from validators import ValidationError


def normalize_url(url):
    parsed_url = urlparse(url)
    return parsed_url._replace(
        path='', params='', query='', fragment='').geturl()


def is_url_correct(url):
    return not isinstance(validate_url(url), ValidationError)
