
import os

from apiflask import APIFlask, Schema
from apiflask.fields import String

app = APIFlask('greeting', title='Greeting Service')

class PersonData(Schema):
    name = String(required=True)
    title = String()
    description = String()
    
class Message(Schema):
    message = String()

@app.get("/formatGreeting")
@app.input(PersonData, "query")
@app.output(Message)
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
    return { "message": greeting }

if __name__ == "__main__":
    port = 0 if "DYNAMIC_PORTS" in os.environ else 5002
    app.run(port=port)
