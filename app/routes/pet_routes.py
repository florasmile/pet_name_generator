from flask import Blueprint, request, abort, make_response
from ..db import db
from ..models.pet import Pet
from google import genai
import os

client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
bp = Blueprint("pets", __name__, url_prefix="/pets")


@bp.post("")
def create_pet():
    request_data = request.get_json()
    pet_data = generate_pet_name(request_data)
    pet_obj = Pet.from_dict(pet_data)
    db.session.add(pet_obj)
    db.session.commit()

    return pet_obj.to_dict()

def generate_pet_name(request_data):
    # privide the input message for AI API
    if "name" in request_data:
        return request_data
    input_message = f"I need to come up with a name for a pet. The animal type is {request_data["animal"]}, the personality is {request_data["personality"]}, and color is {request_data["coloration"]}. Please help generate a pet name based on those attributes. Please give me just one name please."
    # call client method to get response
    response = client.models.generate_content(model="gemini-1.5-flash", contents=input_message)

    name = response.text.strip("\n")

    print(name)
    request_data["name"] = name
    return request_data
@bp.get("")
def get_pets():
    pet_query = db.select(Pet)

    pets = db.session.scalars(pet_query)
    response = []

    for pet in pets:
        response.append(pet.to_dict())

    return response

@bp.get("/<pet_id>")
def get_single_pet(pet_id):
    pet = validate_model(Pet,pet_id)
    return pet.to_dict()

def validate_model(cls,id):
    try:
        id = int(id)
    except:
        response =  response = {"message": f"{cls.__name__} {id} invalid"}
        abort(make_response(response , 400))

    query = db.select(cls).where(cls.id == id)
    model = db.session.scalar(query)
    if model:
        return model

    response = {"message": f"{cls.__name__} {id} not found"}
    abort(make_response(response, 404))