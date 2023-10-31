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

from io import BytesIO
import json

import click

from json_fg_validator.json_fg.ets import JSONFGTestSuite
from json_fg_validator.util import (get_cli_common_options, parse_json_fg,
                                    setup_logger, urlopen_)


@click.group()
def ets():
    """executable test suite"""
    pass


@click.command()
@click.pass_context
@get_cli_common_options
@click.argument('file_or_url')
@click.option('--fail-on-schema-validation/--no-fail-on-schema-validation',
              '-f', default=True,
              help='Stop the ETS on failing schema validation')
def validate(ctx, file_or_url, logfile, verbosity,
             fail_on_schema_validation=True):
    """validate against the abstract test suite"""

    setup_logger(verbosity, logfile)

    click.echo(f'Opening {file_or_url}')

    if file_or_url.startswith('http'):
        content = BytesIO(urlopen_(file_or_url).read())
    else:
        content = file_or_url

    click.echo(f'Validating {file_or_url}')

    try:
        data = parse_json_fg(content)
    except Exception as err:
        raise click.ClickException(err)

    click.echo('Detected JSON FG')
    ts = JSONFGTestSuite(data)
    try:
        results = ts.run_tests(fail_on_schema_validation)
    except Exception as err:
        raise click.ClickException(err)

    click.echo(json.dumps(results, indent=4))


ets.add_command(validate)
