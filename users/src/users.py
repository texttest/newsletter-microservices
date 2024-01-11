
import os, json
from database import Person
from apiflask import APIFlask, abort, Schema
from apiflask.fields import String
import yaml

app = APIFlask('users', title='Users Service')

class PersonOut(Schema):
    name = String()
    title = String(allow_none=True)
    description = String(allow_none=True)
    first_time_user = bool()

class PersonIn(Schema):
    name = String()
    title = String(allow_none=True)
    description = String(allow_none=True)

@app.post("/persons")
@app.output(PersonOut)
@app.input(PersonIn)
def get_person_http(json_data):
    name = json_data.get('name')
    first_time_user = False
    person = Person.get(name)
    if person is None:
        if name in ["Neonicotinoid", "Insecticide", "DDT"]:
            abort(400, f"{name}s are not kind to bees.")
        person = Person()
        person.name = name
        person.title = json_data.get('title')
        person.description = json_data.get('description')
        person.save() 
        first_time_user = True   
    response = {
        'name': person.name,
        'title': person.title,
        'description': person.description,
        'first_time_user': first_time_user
    }
    return response

if __name__ == "__main__":
    port = 0 if "DYNAMIC_PORTS" in os.environ else 5001
    if "DUMP_SCHEMA" in os.environ:
        print("Writing schema file")
        with open(os.path.join(os.path.dirname(__file__), "users-openapi.yaml"), "w") as f:
            yaml.dump(app.spec, f)
    app.run(port=port)
