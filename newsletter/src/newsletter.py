
import os, json
import requests

from flask_cors import CORS, cross_origin
from apiflask import APIFlask

app = APIFlask('newsletter')
CORS(app)
cpmock_server = os.getenv("CAPTUREMOCK_SERVER")
if cpmock_server:
    app.config['SWAGGER_UI_CONFIG'] = {
        'requestInterceptor': "(req) => { req.url = req.url.replace(/http:..localhost:[0-9]+/, '" + cpmock_server + "'); return req; }"
    }

@app.get("/sayHello/<string:name>")
@cross_origin()
def say_hello(name):
    person = get_person(name)
    resp = format_greeting(person)
    return resp


def get_person(name):
    users_url = os.getenv("USERS_URL", 'http://localhost:5001')
    url = f'{users_url}/getPerson/{name}'
    res = _get(url)
    person = json.loads(res)
    return person


def format_greeting(person):
    greeting_url = os.getenv("GREETING_URL", 'http://localhost:5002')
    url = greeting_url + '/formatGreeting'
    return _get(url, params=person)


def _get(url, params=None):
    r = requests.get(url, params=params)
    assert r.status_code == 200
    return r.text


if __name__ == "__main__":
    port = 0 if "DYNAMIC_PORTS" in os.environ else 5010
    app.run(port=port)
