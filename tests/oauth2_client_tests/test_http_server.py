import logging
import unittest

import requests

from oauth2_client.http_server import start_http_server, stop_http_server

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)5s - %(name)s -  %(message)s')


class TestServer(unittest.TestCase):
    PORT = 8080

    SERVER = None

    CALLBACK_CONTAINER = dict()

    @classmethod
    def setUpClass(cls):
        TestServer.SERVER = start_http_server(TestServer.PORT, callback=TestServer.CALLBACK_CONTAINER.update)

    @classmethod
    def tearDownClass(cls):
        if TestServer.SERVER is not None:
            stop_http_server(TestServer.SERVER)

    def test_start(self):
        response = requests.get('http://127.0.0.1:%d' % TestServer.PORT, proxies=dict(http=''))
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)

    def test_response_no_parameter(self):
        response = requests.get('http://127.0.0.1:%d' % TestServer.PORT, proxies=dict(http=''))
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(response.text, '{}')

    def test_response_parameter(self):
        response = requests.get('http://127.0.0.1:%d?toto=titi' % TestServer.PORT, proxies=dict(http=''))
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        _logger.debug("test_response_parameter - %s", response.text)
        obj_response = response.json()
        self.assertIsNotNone(obj_response)
        self.assertEqual(obj_response.get('toto', None), 'titi')

    def test_callback_parameter(self):
        TestServer.CALLBACK_CONTAINER.clear()
        response = requests.get('http://127.0.0.1:%d?toto=titi' % TestServer.PORT, proxies=dict(http=''))
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers['Content-Type'], 'application/json')
        self.assertEqual(TestServer.CALLBACK_CONTAINER.get('toto', None), 'titi')
