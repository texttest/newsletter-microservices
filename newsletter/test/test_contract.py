import pytest
import os
from specmatic.core.specmatic import Specmatic

from src.newsletter import app

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app_host = "127.0.0.1"
app_port = 5010
stub_host = "127.0.0.1"
stub_port = 9000

os.environ['USERS_URL'] = 'http://' + stub_host + ':' + str(stub_port)
os.environ['GREETING_URL'] = 'http://' + stub_host + ':' + str(stub_port)

expectation_json_file = ROOT_DIR + '/test/data'

class TestContract:
    pass

Specmatic() \
    .with_project_root(ROOT_DIR) \
    .with_stub(stub_host, stub_port, args=["--data="+expectation_json_file]) \
    .with_wsgi_app(app, app_host, app_port) \
    .test(TestContract) \
    .run()

if __name__ == '__main__':
    pytest.main()