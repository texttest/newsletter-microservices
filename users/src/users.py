
import os, json
from database import Person
from apiflask import APIFlask, abort

app = APIFlask('users', title='Users Service')

@app.get("/getPerson/<string:name>")
def get_person_http(name):
    person = Person.get(name)
    if person is None:
        if name in ["Neonicotinoid", "Insecticide", "DDT"]:
            abort(400, f"{name}s are not kind to bees.")
        person = Person()
        person.name = name
        person.save()
    else:
        person.description
    response = {
        'name': person.name,
        'title': person.title,
        'description': person.description,
    }
    return json.dumps(response)

if __name__ == "__main__":
    port = 0 if "DYNAMIC_PORTS" in os.environ else 5001
    app.run(port=port)
