
import os

from apiflask import APIFlask, Schema
from apiflask.fields import String
#import yaml

app = APIFlask('greeting', title='Greeting Service')

class PersonData(Schema):
    name = String(required=True)
    title = String()
    description = String()
    

@app.get("/formatGreeting")
#@app.output(StringSchema, content_type="text/html", status_code=200)
@app.input(PersonData, "query")
def format_greeting(query_data):
    name = query_data.get('name')
    title = query_data.get('title')
    description = query_data.get('description')
        
    greeting = 'Hello'
    greeting += ', '
    if title:
        greeting += title + ' '
    greeting += name + '!'
    if description:
        greeting += ' ' + description + " is my favourite!"
    return greeting

if __name__ == "__main__":
    port = 0 if "DYNAMIC_PORTS" in os.environ else 5002
    # with open(os.path.join(os.path.dirname(__file__), "openapi.yaml"), "w") as f:
    #     yaml.dump(app.spec, f)
    app.run(port=port)
