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

from jsonschema.validators import Draft202012Validator

from json_fg_validator.bundle import JSON_FG_FILES

LOGGER = logging.getLogger(__name__)


def gen_test_id(test_id: str) -> str:
    """
    Convenience function to print test identifier as URI

    :param test_id: test suite identifier

    :returns: test identifier as URI
    """

    return f'http://www.opengis.net/spec/json-fg-1/0.2/{test_id}'


class JSONFGTestSuite:
    """Test suite for JSON FG"""

    def __init__(self, data: dict):
        """
        initializer

        :param data: dict of JSON FG

        :returns: `json_fg_validator.ets.JSONFGTestSuite'
        """

        self.test_id = None
        self.data = data
        self.report = []

    def run_tests(self, fail_on_schema_validation=False):
        """Convenience function to run all tests"""

        results = []
        tests = []
        ets_report = {
            'summary': {},
        }

        for f in dir(JSONFGTestSuite):
            if all([
                    callable(getattr(JSONFGTestSuite, f)),
                    f.startswith('test_requirement')]):

                tests.append(f)

        validation_result = self.test_requirement_validation()
        if validation_result['code'] == 'FAILED':
            if fail_on_schema_validation:
                msg = ('Record fails JSON FG validation. Stopping ETS ',
                       f"errors: {validation_result['errors']}")
                LOGGER.error(msg)
                raise ValueError(msg)

        for t in tests:
            results.append(getattr(self, t)())

        for code in ['PASSED', 'FAILED', 'SKIPPED']:
            r = len([t for t in results if t['code'] == code])
            ets_report['summary'][code] = r

        ets_report['tests'] = results

        return {
            'ets-report': ets_report
        }

    def test_requirement_validation(self):
        """
        Validate that a JSON FG record is valid to the authoritative
        JSON-FG schema
        """

        validation_errors = []

        status = {
            'id': gen_test_id('req/core/schema-valid'),
            'code': 'PASSED'
        }

        if self.data['type'] == 'Feature':
            schema = 'feature.json'
        elif self.data['type'] == 'FeatureCollection':
            schema = 'featurecollection.json'

        schema = JSON_FG_FILES / 'json-fg' / '0.1.1' / schema

        if not schema.exists():
            msg = "JSON FG schemas missing. Run 'json-fg-validator bundle sync' to cache"  # noqa
            LOGGER.error(msg)
            raise RuntimeError(msg)

        with schema.open() as fh:
            LOGGER.debug(f'Validating {self.data} against {schema}')
            validator = Draft202012Validator(json.load(fh))

            for error in validator.iter_errors(self.data):
                LOGGER.debug(f'{error.json_path}: {error.message}')
                validation_errors.append(f'{error.json_path}: {error.message}')

            if validation_errors:
                status['code'] = 'FAILED'
                status['message'] = f'{len(validation_errors)} error(s)'
                status['errors'] = validation_errors

        return status

    def test_requirement_conformance(self):
        """
        Validate that a JSON FG provides valid conformance information.
        """

        found = False

        status = {
            'id': gen_test_id('req/core/metadata'),
            'code': 'PASSED'
        }

        conformance_classes = [
            'http://www.opengis.net/spec/json-fg-1/0.2/conf/core',
            '[ogc-json-fg-1-0.2:core]'
        ]

        conformance = self.data.get('conformsTo')

        if conformance is None:
            status['code'] = 'FAILED'
            status['message'] = 'Missing conformsTo member'

        for cc in conformance_classes:
            if cc in conformance:
                found = True
                break

        if not found:
            status['code'] = 'FAILED'
            status['message'] = 'Missing valid conformsTo member'

        return status

    def test_requirement_temporal_instant(self):
        """
        Validate that a JSON FG provides valid temporal instant information.
        """

        status = {
            'id': gen_test_id('req/core/instant'),
            'code': 'PASSED',
            'message': 'Passes given data is compliant/valid to schema'
        }

        return status

    def test_requirement_temporal_interval(self):
        """
        Validate that a JSON FG provides valid temporal interval information.
        """

        status = {
            'id': gen_test_id('req/core/interval'),
            'code': 'PASSED',
            'message': 'Passes given data is compliant/valid to schema'
        }

        return status

    def test_requirement_temporal_instant_and_interval(self):
        """
        Validate that a JSON FG provides valid temporal instant and
        interval information.
        """

        status = {
            'id': gen_test_id('req/core/instant-and-interval'),
            'code': 'PASSED'
        }

        time_ = self.data.get('time')
        if time_ is None:
            status['code'] = 'SKIPPED'
            status['message'] = 'Skipping given time is null'
            return status

        if 'date' in time_ and 'timestamp' in time_:
            if time_['date'] != time_['timestamp']:
                status['code'] = 'FAILED'
                status['message'] = 'date and timestamp not identical'

        if 'timestamp' in time_ and 'interval' in time_:
            found = False

            for int_ in time_['interval']:
                if int_ == time_['timestamp']:
                    found = True

            if not found:
                status['code'] = 'FAILED'
                status['message'] = 'timestamp not in interval'

        return status
