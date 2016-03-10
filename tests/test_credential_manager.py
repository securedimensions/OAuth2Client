from oauth2_client.credentials_manager import CredentialManager, ServiceInformation, OAuthError
from oauth2_client.http_server import read_request_parameters
import unittest
import httplib
import SocketServer
import BaseHTTPServer
import logging
import threading
import requests

_logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG,
                    format='%(levelname)5s - %(name)s -  %(message)s')

authorize_server_port = 8080
token_server_port = 8081
api_server_port = 8082
redirect_server_port = 8090

service_information = ServiceInformation('http://localhost:%d' % authorize_server_port,
                                         'http://localhost:%d' % token_server_port,
                                         'http://localhost:%d' % api_server_port,
                                         '/oauth/authorize',
                                         '/oauth/token',
                                         'client_id_test',
                                         'client_secret_test',
                                         ['scope1', 'scope2'])


class FakeAuthorizeHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    CODE = '123'

    def do_GET(self):
        _logger.debug('AuthorizeHandler - GET - %s' % self.path)
        if self.path == service_information.authorize_uri \
                or self.path.index('%s?' % service_information.authorize_uri) != 0:
            self.send_response(httplib.NOT_FOUND, 'Not Found')
        else:
            params_received = read_request_parameters(self.path)
            self._check_parameters(params_received)
            redirect_uri = params_received.get('redirect_uri', None)
            state = params_received.get('state', '')
            if redirect_uri is not None:
                _logger.debug('AuthorizeHandler - redirect - %s', redirect_uri)
                self.send_response(httplib.SEE_OTHER, 'Redirect')
                self.send_header("Location", '%s?code=%s&state=%s' % (redirect_uri, FakeAuthorizeHandler.CODE, state))
            else:
                self.send_response(httplib.BAD_REQUEST, 'Bad Request')
        self.send_header("Content-Length", 0)
        self.end_headers()
        self.wfile.close()

    def _check_parameters(self, parameters):
        pass


def start_server(port, handler_class):
    httpd = SocketServer.TCPServer(('', port), handler_class)

    def serve():
        httpd.serve_forever()

    thread_type = threading.Thread(target=serve)
    thread_type.start()
    return httpd


def stop_server(httpd):
    httpd.shutdown()


class TestManager(unittest.TestCase):
    def test_authorize_ok(self):
        def equal_assertion(val1, val2):
            self.assertEqual(val1, val2)

        class CheckAuthorizeHandler(FakeAuthorizeHandler):
            def _check_parameters(self, parameters):
                _logger.debug('CheckAuthorizeHandler - _check_parameters - %s', str(parameters))
                equal_assertion(parameters.get('redirect_uri', None), 'http://localhost:%d' % redirect_server_port)
                equal_assertion(parameters.get('state', None), 'state_test')
                equal_assertion(parameters.get('client_id', None), 'client_id_test')
                equal_assertion(parameters.get('scope', None), 'scope1 scope2')

        authorize_server = start_server(authorize_server_port, CheckAuthorizeHandler)
        manager = None
        try:
            manager = CredentialManager(service_information, proxies=dict(http=''))
            url = manager.init_authorize_code_process('http://localhost:%d' % redirect_server_port, 'state_test')
            self.assertIsNotNone(url)
            requests.get(url, proxies=dict(http=''))
            code = manager.terminate_authorize_code_process()
            manager = None
            equal_assertion(code, FakeAuthorizeHandler.CODE)
        finally:
            stop_server(authorize_server)
            if manager is not None and manager.authorization_code_context is not None:
                manager.terminate_authorize_code_process(0.1)

    def test_authorize_ko(self):
        def equal_assertion(val1, val2):
            self.assertEqual(val1, val2)

        class CheckAuthorizeHandlerbadState(FakeAuthorizeHandler):
            def _check_parameters(self, parameters):
                equal_assertion(parameters.get('redirect_uri', None), 'http://localhost:%d' % redirect_server_port)
                equal_assertion(parameters.get('state', None), 'state_test')
                parameters['state'] = 'other_state'

        _logger.debug('test_authorize_ko - starting server')
        authorize_server = start_server(authorize_server_port, CheckAuthorizeHandlerbadState)
        _logger.debug('test_authorize_ko - server started')
        manager = None
        try:
            manager = CredentialManager(service_information, proxies=dict(http=''))
            url = manager.init_authorize_code_process('http://localhost:%d' % redirect_server_port, 'state_test')
            self.assertIsNotNone(url)
            _logger.debug('Url got = %s', url)
            requests.get(url, proxies=dict(http=''))
            self.assertRaises(OAuthError, manager.terminate_authorize_code_process)
        finally:
            stop_server(authorize_server)
            if manager is not None and manager.authorization_code_context is not None:
                manager.terminate_authorize_code_process(0.1)
