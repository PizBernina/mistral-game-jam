import os
from mistralai import Mistral
from helper_functions import load_character_data
from dotenv import load_dotenv
load_dotenv()

api_key = os.environ["MISTRAL_API_KEY"]
client = Mistral(api_key=api_key)
model = "mistral-large-latest"
trump_character = load_character_data()
