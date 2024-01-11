
import os, json
import requests

from flask_cors import CORS, cross_origin
from apiflask import APIFlask, abort, Schema
from apiflask.fields import String
import yaml

app = APIFlask('newsletter', title='Newsletter Service')
CORS(app)
cpmock_server = os.getenv("CAPTUREMOCK_SERVER")
if cpmock_server:
    interceptor = "(req) => { req.url = req.url.replace(/http:..127.0.0.1:[0-9]+/, '" + cpmock_server + "'); return req; }"
    app.config['SWAGGER_UI_CONFIG'] = {
        'requestInterceptor': interceptor
    }


class PersonIn(Schema):
    name = String()


@app.post("/sayHello")
@app.input(PersonIn)
@cross_origin()
def say_hello(json_data):
    name = json_data.get('name')
    person = fetch_or_create_person(name)
    return format_greeting(person)


def fetch_or_create_person(name):
    users_url = os.getenv("USERS_URL", 'http://localhost:5001')
    url = f'{users_url}/persons'
    return _post(url, person={'name': name})


def format_greeting(person):
    greeting_url = os.getenv("GREETING_URL", 'http://localhost:5002')
    url = greeting_url + '/formatGreeting'
    return _get(url, params=person)


def _post(url, person):
    r = requests.post(url, json=person)
    data = json.loads(r.text)
    if r.status_code != 200:
        abort(r.status_code, data['message'])
    return data


def _get(url, params=None):
    r = requests.get(url, params=params)
    if r.status_code != 200:
        data = json.loads(r.text)
        abort(r.status_code, data['message'])
    return r.text


if __name__ == "__main__":
    port = 0 if "DYNAMIC_PORTS" in os.environ else 5010
    if "DUMP_SCHEMA" in os.environ:
        print("Writing schema file")
        with open(os.path.join(os.path.dirname(__file__), "newsletter-openapi.yaml"), "w") as f:
            yaml.dump(app.spec, f)
    app.run(port=port)
