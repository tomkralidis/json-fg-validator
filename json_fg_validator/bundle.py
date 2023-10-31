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

import io
import logging
import shutil
import zipfile

import click

from json_fg_validator.util import (get_cli_common_options, get_userdir,
                                    urlopen_, setup_logger)

LOGGER = logging.getLogger(__name__)

USERDIR = get_userdir()

JSON_FG_FILES = get_userdir()


@click.group()
def bundle():
    """Configuration bundle management"""
    pass


@click.command()
@get_cli_common_options
@click.pass_context
def sync(ctx, logfile, verbosity):
    "Sync configuration bundle"""

    setup_logger(verbosity, logfile)
    LOGGER.debug('Caching schemas')

    if USERDIR.exists():
        shutil.rmtree(USERDIR)

    LOGGER.debug(f'Downloading JSON FG schemas to {JSON_FG_FILES}')
    JSON_FG_FILES.mkdir(parents=True, exist_ok=True)

    URL = 'https://beta.schemas.opengis.net/json-fg/json-fg-0_1_1.zip'
    FH = io.BytesIO(urlopen_(URL).read())
    with zipfile.ZipFile(FH) as z:
        z.extractall(JSON_FG_FILES)


bundle.add_command(sync)
