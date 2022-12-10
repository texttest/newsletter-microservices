
import os, json
import requests

from flask_cors import CORS, cross_origin
from apiflask import APIFlask, abort

app = APIFlask('newsletter')
CORS(app)
cpmock_server = os.getenv("CAPTUREMOCK_SERVER")
if cpmock_server:
    interceptor = "(req) => { req.url = req.url.replace(/http:..127.0.0.1:[0-9]+/, '" + cpmock_server + "'); return req; }"
    app.config['SWAGGER_UI_CONFIG'] = {
        'requestInterceptor': interceptor
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
    if r.status_code != 200:
        data = json.loads(r.text)
        abort(r.status_code, data['message'])
    return r.text


if __name__ == "__main__":
    port = 0 if "DYNAMIC_PORTS" in os.environ else 5010
    app.run(port=port)
