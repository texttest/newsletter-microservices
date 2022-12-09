from flask import Flask, request
import os

app = Flask('greeting')

@app.route("/formatGreeting")
def handle_format_greeting():
    name = request.args.get('name')
    title = request.args.get('title')
    descr = request.args.get('description')
    return format_greeting(
        name=name,
        title=title,
        description=descr,
    )

def format_greeting(name, title, description):
    greeting = 'Hello'
    greeting += ', '
    if title:
        greeting += title + ' '
    greeting += name + '!'
    if description:
        greeting += ' ' + description + " is my favourite!"
    return greeting

if __name__ == "__main__":
    port = 0 if "DYNAMIC_PORTS" in os.environ else 3002
    app.run(port=port)
