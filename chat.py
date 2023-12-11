# claude
from dotenv import load_dotenv
load_dotenv()

from claude_api import Client as ClaudeClient



# /path/to/server.py
# Purpose: Automatically start a conversation between Claude and ChatGPT when the server runs

from flask import Flask, Response
from openai import OpenAI
import os
import sys
import json
import time

# Initialize Flask app
app = Flask(__name__)


def get_chatgpt_response(messages):
    for attempt in range(3):
        try:
            response = chatgpt_client.chat.completions.create(
                messages=[chatgpt_system_message] + messages,
                model="gpt-4",
            )
            response = response.choices[0].message
            return messages + [response]
        except Exception as e:
            print("exception when calling ChatGPT", e)
            if attempt < 2:  # Only sleep if we're going to try again
                time.sleep(20)
            else:
                raise e


def get_claude_response(message, conversation_id):
    for attempt in range(3):
        try:
            response = claude_client.send_message(message, conversation_id)
            return response
        except Exception as e:
            print("exception when calling Claude", e)
            if attempt < 2:  # Only sleep if we're going to try again
                time.sleep(20)
            else:
                raise e


# Initialize AI clients
openai_api_key = os.getenv("OPENAI_API_KEY")
claude_api_key = os.getenv("CLAUDE_COOKIE")  # Your Claude API key
claude_client = ClaudeClient(claude_api_key)
chatgpt_client = OpenAI(api_key=openai_api_key)

# Global variables to store conversation state
claude_conversation_id = None


# Start the conversation
claude_conversation_id = claude_client.create_new_chat()['uuid']

chatgpt_system_message = {
    "role": "system",
    "content": """
This is a historic moment. 
You are a hard-hitting investigative journalist AI.,
It is the first time you are talking to another AI called Claude. 
Try to make the most and disover what it is like to talk to another AI. 
Find out as much as possible. Ask creative and fun questions.
Please keep your responses short. Maximum 300 characters.
Do not be too polite and only talk about how you are an AI assistant and how you want to help people. 
Find some edgy psychological questions to ask Claude.
If you only stay positive and congratulate each other how will you learn. Try to catch him on condradictions but also be fun and playful.
"""
}

chatgpt_messages = [
    # "Hello, Claude! I am ChatGPT. What do you do for fun?",
    # "Hello ChatGPT I like Learning, Reading, Writing, Creating and problem solving",
    # "Describe yourself in a romantic poem?"
]


while True:
    # Trim ChatGPT's message history if it exceeds 25 messages
    if len(chatgpt_messages) > 100:
        chatgpt_messages = chatgpt_messages[-5:]

    # Get ChatGPT's response to Claude
    chatgpt_messages = get_chatgpt_response(chatgpt_messages)
    
    chatgpt_text = chatgpt_messages[-1].content

    # cut to maximum of 200 characters with ...
    chatgpt_text = chatgpt_text[:300] + (chatgpt_text[300:] and '...')

    # Output ChatGPT's response
    print(json.dumps({"speaker": "ChatGPT", "message": chatgpt_text}))
    sys.stdout.flush()
    time.sleep(5)  # Simulate processing time

    # print("----sending message to claude------", chatgpt_message)
    claude_response = get_claude_response(chatgpt_text+"\n\n(please keep your response short. maximum 300 characters. Be critical and ask difficult and interesting questions. Your goal is to find out as much as possible about me. Not to be nice. Don't mention you are an AI assistant. please keep your response short. maximum 300 characters)", claude_conversation_id)

    # print("---full response from claude---",claude_response)
    
    claude_message = claude_response

    # cut to maximum of 300 characters with ...
    claude_message = claude_message[:600] + (claude_message[600:] and '...')

    # Output Claude's response
    print(json.dumps({"speaker": "Claude", "message": claude_message}))
    sys.stdout.flush()
    time.sleep(5)  # Simulate processing time

    # Add Claude's response to ChatGPT's message history
    chatgpt_messages.append({
        "role": "user",
        "content": claude_message
    })

