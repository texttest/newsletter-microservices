
import os

from apiflask import APIFlask, Schema
from apiflask.fields import String
import yaml

app = APIFlask('greeting', title='Greeting Service')

class PersonData(Schema):
    name = String(required=True)
    title = String()
    description = String()
    first_time_user = bool()
    
@app.get("/formatGreeting")
@app.input(PersonData, "query")
def format_greeting(query_data):
    name = query_data.get('name')
    title = query_data.get('title')
    description = query_data.get('description')
    first_time_user = query_data.get('first_time_user') 
        
    greeting = 'Hello'
    greeting += ', '
    if title:
        greeting += title + ' '
    greeting += name + '!'
    if description:
        greeting += ' ' + description + " is my favourite!"
    if first_time_user:
        greeting += ' Nice to meet you!'
    else:
        greeting += ' Welcome back!'
    return greeting

if __name__ == "__main__":
    port = 0 if "DYNAMIC_PORTS" in os.environ else 5002
    if "DUMP_SCHEMA" in os.environ:
        print("Writing schema file")
        with open(os.path.join(os.path.dirname(__file__), "greeting-openapi.yaml"), "w") as f:
            yaml.dump(app.spec, f)
    app.run(port=port)
