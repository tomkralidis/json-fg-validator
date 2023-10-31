###################################################################
#
# Authors: Tom Kralidis <tomkralidis@gmail.com>
#
# Copyright (c) 2023 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
###################################################################

import json
import logging
from pathlib import Path
import ssl
import sys
from urllib.error import URLError
from urllib.request import urlopen
from urllib.parse import urlparse

LOGGER = logging.getLogger(__name__)
THISDIR = Path(__file__).parent.resolve()


def get_cli_common_options(function):
    """
    Define common CLI options
    """

    import click
    function = click.option('--verbosity', '-v',
                            type=click.Choice(
                                ['ERROR', 'WARNING', 'INFO', 'DEBUG']),
                            help='Verbosity')(function)
    function = click.option('--log', '-l', 'logfile',
                            type=click.Path(writable=True, dir_okay=False),
                            help='Log file')(function)
    return function


def get_userdir() -> str:
    """
    Helper function to get userdir

    :returns: user's home directory
    """

    return Path.home() / '.json-fg-validator'


def setup_logger(loglevel: str = None, logfile: str = None) -> None:
    """
    Setup logging

    :param loglevel: logging level
    :param logfile: logfile location

    :returns: void (creates logging instance)
    """

    if loglevel is None and logfile is None:  # no logging
        return

    if loglevel is None and logfile is not None:
        loglevel = 'INFO'

    log_format = \
        '[%(asctime)s] %(levelname)s - %(message)s'
    date_format = '%Y-%m-%dT%H:%M:%SZ'

    loglevels = {
        'CRITICAL': logging.CRITICAL,
        'ERROR': logging.ERROR,
        'WARNING': logging.WARNING,
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'NOTSET': logging.NOTSET,
    }

    loglevel = loglevels[loglevel]

    if logfile is not None:  # log to file
        logging.basicConfig(level=loglevel, datefmt=date_format,
                            format=log_format, filename=logfile)
    elif loglevel is not None:  # log to stdout
        logging.basicConfig(level=loglevel, datefmt=date_format,
                            format=log_format, stream=sys.stdout)
        LOGGER.debug('Logging initialized')


def urlopen_(url: str):
    """
    Helper function for downloading a URL

    :param url: URL to download

    :returns: `http.client.HTTPResponse`
    """

    try:
        response = urlopen(url)
    except (ssl.SSLError, URLError) as err:
        LOGGER.warning(err)
        LOGGER.warning('Creating unverified context')
        context = ssl._create_unverified_context()

        response = urlopen(url, context=context)

    return response


def check_url(url: str, check_ssl: bool, timeout: int = 30) -> dict:
    """
    Helper function to check link (URL) accessibility

    :param url: The URL to check
    :param check_ssl: Whether the SSL/TLS layer verification shall be made
    :param timeout: timeout, in seconds (default: 30)

    :returns: `dict` with details about the link
    """

    response = None
    result = {
        'mime-type': None,
        'url-original': url
    }

    try:
        if not check_ssl:
            LOGGER.debug('Creating unverified context')
            result['ssl'] = False
            context = ssl._create_unverified_context()
            response = urlopen(url, context=context, timeout=timeout)
        else:
            response = urlopen(url, timeout=timeout)
    except TimeoutError as err:
        LOGGER.debug(f'Timeout error: {err}')
    except (ssl.SSLError, URLError, ValueError) as err:
        LOGGER.debug(f'SSL/URL error: {err}')
        LOGGER.debug(err)
    except Exception as err:
        LOGGER.debug(f'Other error: {err}')
        LOGGER.debug(err)

    if response is None and check_ssl:
        return check_url(url, False)

    if response is not None:
        result['url-resolved'] = response.url
        parsed_uri = urlparse(response.url)
        if parsed_uri.scheme in ('http', 'https'):
            if response.status > 300:
                LOGGER.debug(f'Request failed: {response}')
            result['accessible'] = response.status < 300
            result['mime-type'] = response.headers.get_content_type()
        else:
            result['accessible'] = True
        if parsed_uri.scheme in ('https') and check_ssl:
            result['ssl'] = True
    else:
        result['accessible'] = False
    return result


def parse_json_fg(content: str) -> dict:
    """
    Parse a buffer into a JSON dict (JSON-FG)

    :param content: str of JSON

    :returns: `dict` object of JSON FG
    """

    LOGGER.debug('Attempting to parse as JSON')
    try:
        with open(content) as fh:
            data = json.load(fh)
    except json.decoder.JSONDecodeError as err:
        LOGGER.error(err)
        raise RuntimeError(f'Encoding error: {err}')

    return data
