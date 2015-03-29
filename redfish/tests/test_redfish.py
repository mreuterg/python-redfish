# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_redfish
----------------------------------

Tests for `redfish` module.
"""

import fixtures
import httplib
import mock
import ssl

from redfish.tests import base
from redfish import connection


def get_fake_params(host=None, user=None, pword=None):
    if not host:
        host = 'https://127.0.0.1'
    if not user:
        user = 'admin'
    if not pword:
        pword = 'password'
    return (host, user, pword)


def get_response():
    class _response(object):
        status = 200
        def read(self):
            return "{'foo': 'bar'}"
        def getheaders(self):
            return [('Fake-Header', 'fake value')]
    return _response()


class TestException(Exception):
    pass


class TestRedfishConnection(base.TestCase):

    def setUp(self):
        super(TestRedfishConnection, self).setUp()
        self.log_fixture = self.useFixture(fixtures.FakeLogger())
        self.con_mock = mock.MagicMock()
        self.con_mock.getresponse = get_response

        self.http_mock = mock.patch.object(httplib, 'HTTPConnection').start()
        self.http_mock.return_value = self.con_mock
        self.https_mock = mock.patch.object(httplib, 'HTTPSConnection').start()
        self.https_mock.return_value = self.con_mock
        self.addCleanup(self.http_mock.stop)
        self.addCleanup(self.https_mock.stop)

    def test_create_ok(self):
        con = connection.RedfishConnection(*get_fake_params())
        self.assertEqual(1, self.https_mock.call_count)
        self.assertEqual(0, self.http_mock.call_count)

    def test_create_calls_https_connect(self):
        self.https_mock.side_effect = TestException()
        self.assertRaises(TestException,
                          connection.RedfishConnection,
                          *get_fake_params(host='https://fake'))

    def test_create_calls_http_connect(self):
        self.http_mock.side_effect = TestException()
        self.assertRaises(TestException,
                          connection.RedfishConnection,
                          *get_fake_params(host='http://fake'))

# FIXME: ssl module has no attribute 'SSLContext'
# NOTE: skip this test if sys.version_info (major, minor) != (2, 7) and micro < 9
#    @mock.patch.object(ssl, 'SSLContext')
#    def test_insecure_ssl(self, ssl_mock):
#        ssl_mock.return_value = mock.Mock()
#        con = connection.RedfishConnection(*get_fake_params)
#        ssl_mock.assert_called_once_with(ssl.PROTOCOL_TLSv1)
