
import os

from apiflask import APIFlask, Schema
from apiflask.fields import String

app = APIFlask('greeting', title='Greeting Service')

class PersonData(Schema):
    name = String(required=True)
    title = String()
    description = String()

@app.get("/formatGreeting")
@app.input(PersonData, "query")
def format_greeting(query):
    name = query.get('name')
    title = query.get('title')
    description = query.get('description')
        
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
    app.run(port=port)
