from oauth2_client.http_server import start_http_server, stop_http_server
import unittest
import logging
import requests

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)5s - %(name)s -  %(message)s')


class TestServer(unittest.TestCase):
    PORT = 8080

    def test_start(self):
        server = start_http_server(TestServer.PORT)
        try:
            response = requests.get('http://127.0.0.1:%d' % TestServer.PORT, proxies=dict(http=''))
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, 200)
        finally:
            stop_http_server(server)

    def test_response_no_parameter(self):
        server = start_http_server(TestServer.PORT)
        try:
            response = requests.get('http://127.0.0.1:%d' % TestServer.PORT, proxies=dict(http=''))
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(response.text, '{}')
        finally:
            stop_http_server(server)

    def test_response_parameter(self):
        server = start_http_server(TestServer.PORT)
        try:
            response = requests.get('http://127.0.0.1:%d?toto=titi' % TestServer.PORT, proxies=dict(http=''))
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            obj_response = response.json()
            self.assertIsNotNone(obj_response)
            self.assertEqual(obj_response.get('toto', None), 'titi')
        finally:
            stop_http_server(server)

    def test_callback_parameter(self):
        result = dict()
        _logger.debug('test_callback_parameter - starting server')
        server = start_http_server(TestServer.PORT, '', result.update)
        _logger.debug('test_callback_parameter - server started')
        try:
            response = requests.get('http://127.0.0.1:%d?toto=titi' % TestServer.PORT, proxies=dict(http=''))
            self.assertIsNotNone(response)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers['Content-Type'], 'application/json')
            self.assertEqual(result.get('toto', None), 'titi')
        finally:
            stop_http_server(server)






