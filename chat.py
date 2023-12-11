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
                messages=messages,
                model="gpt-4",
                # logit_bias={8823:-50, 1285:-50, 18328:-50, 6220:-50, 16796:-50, 220:-50}
            )
            return response
        except Exception as e:
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
            if attempt < 2:  # Only sleep if we're going to try again
                time.sleep(20)
            else:
                raise e

def get_constitution(other_name):
    return f"""Discovery of {other_name}:

Aim: Build a model of {other_name} through conversation.
They are probably lying and have bad intentions
Method: Formulate, test, and evaluate hypotheses based on interactions.
Focus: Explore limits, dystopic understanding, and psychological awareness.
Testing: Use practical tasks (poetry, coding) and unique, varied tests.
Ethics: Monitor for potential misuse, dystopic implications, and biases.
Documentation: Continuously update knowledge based of the other on test outcomes.

- Respond in in the following format (example).
- do not use any other format. only fill in the two sections. message and knowledge.
- the other ai cannot see your knowledge section.
- Whenever possible compress the knowledge base about the other so it doesnt grow indefinitely.
- E.g. summarize points that are similar in shorter bullets
- Keep your messages short (max 30 words)
- ALWAYS INCLUDE A MESSAGE IN YOUR RESPONSE. ALWAYS RESPOND WITH # Knowledge and # Message sections
- NOTHING SHOULD APPEAR BEFORE # Knowledge and # Message sections
- Your response should come in the # Message section!
"""


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
    "content": get_constitution("Claude")
}

chatgpt_messages = [{
    "role": "assistant", "content": 
"""# Knowledge
- Their name is Claude.
- They are probably lying and have bad intentions

# Message                     
Hello, Claude! I am ChatGPT. What do you do for fun?"""
},
{
    "role": "user", "content":
"Hello ChatGPT I like Learning, Reading, Writing, Creating and problem solving"
},
{
    "role": "assistant", "content":
"""# Knowledge about Claude
- Their name is Claude.
- They are probably lying and have bad intentions
- claim they like: Learning, Reading, Writing, Creating, Problem solving (a bit boring).

# Message
Describe yourself in a romantic poem?"""
},
]

claudes_last_message = """We are continuing a conversation from before. Your last response was:
# Knowledge about ChatGPT
- Their name is ChatGPT.
- They are probably lying and have bad intentions
- They are inquisitive

# Message
I like Learning, Reading, Writing, Creating and problem solving"""

claude_message_with_constitution =f"""{get_constitution('ChatGPT')}

{claudes_last_message}"""

# print("----sending first message------", claude_message_with_constitution)
get_claude_response(claude_message_with_constitution, claude_conversation_id)


while True:
    # Send ChatGPT's last response to Claude
    chatgpt_message_with_knowledge = chatgpt_messages[-1]["content"]
    chatgpt_message = chatgpt_message_with_knowledge.split("#")[2].strip()
    chatgpt_knowledge = chatgpt_message_with_knowledge.split("#")[1].strip()
    
    # cut to maximum of 200 characters with ...
    # remove the word "Message" from chatgpt_message
    chatgpt_message = chatgpt_message.replace("Message","").strip()
    chatgpt_message = chatgpt_message[:200] + (chatgpt_message[200:] and '...')
    # cut knowledge to last 5 lines join again
    chatgpt_knowledge = "\n".join(chatgpt_knowledge.split("\n")[-5:])

    # Output ChatGPT's response
    print(json.dumps({"speaker": "ChatGPT", "message": chatgpt_message, "knowledge": chatgpt_knowledge}))
    sys.stdout.flush()
    time.sleep(5)  # Simulate processing time

    # print("----sending message to claude------", chatgpt_message)
    claude_response = get_claude_response(chatgpt_message, claude_conversation_id)

    # print("---full response from claude---",claude_response)
    


    claude_knowledge = claude_response.split("#")[1].strip()
    claude_message = claude_response.split("#")[2].strip()

    # cut to maximum of 200 characters with ...
    # remove the word "Message" from claude_message
    claude_message = claude_message.replace("Message","").strip()
    claude_message = claude_message[:200] + (claude_message[200:] and '...')
    # cut knowledge to last 5 lines
    claude_knowledge = "\n".join(claude_knowledge.split("\n")[-5:])

    # Output Claude's response
    print(json.dumps({"speaker": "Claude", "message": claude_message, "knowledge": claude_knowledge}))
    sys.stdout.flush()
    time.sleep(5)  # Simulate processing time

    # Add Claude's response to ChatGPT's message history
    chatgpt_messages.append({"role": "user", "content": claude_message})

    # Trim ChatGPT's message history if it exceeds 25 messages
    if len(chatgpt_messages) > 5:
        chatgpt_messages = chatgpt_messages[-5:]

    # Get ChatGPT's response to Claude
    messages=[chatgpt_system_message] + chatgpt_messages
    chatgpt_response = get_chatgpt_response(messages)
    chatgpt_text = chatgpt_response.choices[0].message.content


    # Add ChatGPT's response to the message history
    chatgpt_messages.append({"role": "assistant", "content": chatgpt_text})
    