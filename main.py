import os
import json
from dotenv import load_dotenv
from mistralai import Mistral
from prompts.instruction_prompts import instruction_prompt
from prompts.game_rules import game_rules
from prompts.triggers import triggers
from helper_functions import load_character_data, load_chat_history, save_chat_history
from utils import api_key, model, trump_character, client
load_dotenv()

# Get user message from your existing code
user_message = "Biden for president" 

# Load existing chat history
chat_history = load_chat_history()
# Add user message to history
chat_history.append({
    "role": "user",
    "message": user_message
})

# Whole Prompt
formatted_prompt = instruction_prompt.format(
    chat_history=chat_history,
    character=trump_character,
    rules=game_rules,
    triggers=triggers
)

chat_response = client.chat.complete(
    model=model,
    messages=[
        {
            "role": "system",
            "content": formatted_prompt
        },
        {
            "role": "user",
            "content": user_message
        }
    ]
)

# Get Trump's response
trump_response = chat_response.choices[0].message.content

# Add Trump's response to history
chat_history.append({
    "role": "Trump",
    "message": trump_response
})

# Save updated chat history
save_chat_history(chat_history)

# Print response
print(trump_response)