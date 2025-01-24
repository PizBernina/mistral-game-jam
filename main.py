import os
import json
from dotenv import load_dotenv
from mistralai import Mistral
from prompts.instruction_prompts import instruction_prompt
from prompts.game_rules import game_rules
from prompts.hints import hints
from prompts.triggers import triggers
from helper_functions import load_chat_history, save_chat_history, update_chat_history
from utils import model, trump_character, client

# Get user message from your existing code
user_message = "hello" 

# Load existing chat history
chat_history = load_chat_history()

# Add user message to history
chat_history = update_chat_history(chat_history, user_message=user_message)

# Load Trump character data
#trump_character = load_character_data()

# Whole Prompt
formatted_prompt = instruction_prompt.format(
    hints=hints,
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
chat_history = update_chat_history(chat_history, trump_message=trump_response)


# Save updated chat history
save_chat_history(chat_history)

# Print response
print(trump_response)