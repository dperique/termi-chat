#!/usr/bin/env python

import time
import textwrap
from openai import OpenAI
import json
import os
from datetime import datetime
import glob
import sys

def dashes():
    # Print 80 dashes to separate the user input from the assistant response
    print("\033[1m\033[91m" + "-" * 80 + "\033[0m")

def wrap_text(text, width=80):
    # Function to wrap text except inside code blocks
    wrapped_text = ""
    in_code_block = False
    for line in text.split('\n'):
        if line.startswith("```"):
            in_code_block = not in_code_block
            wrapped_text += line + '\n'
        elif in_code_block:
            wrapped_text += line + '\n'
        else:
            wrapped_text += textwrap.fill(line, width=width) + '\n'
    return wrapped_text

def print_conversation(messages):
    for message in messages:
        dashes()
        timestamp = message.get("timestamp", "202x-xx-xx-xx:xx")
        formatted_text = wrap_text(message['content'])
        print(f"{timestamp} \033[1;32m{message['role'].title()}\033[0m: {formatted_text}")

def save_to_file(messages, filename):
    with open(filename, 'w') as file:
        json.dump(messages, file, indent=2)

def load_from_file(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d-%H:%M")

def get_multiline_input(prompt, user_name="User"):
    print("\033[0;33m" + prompt + "\033[0m")  # Light brown color escape sequence
    print(f"\033[1;32m{user_name}\033[0m, enter your text, then finish with a line containing only Ctrl-D and press Enter.\n")  # Bold green user_name
    lines = []
    while True:
        try:
            line = input()
            if line == "\x04":  # Check if line contains only Ctrl-D
                break
            lines.append(line)
        except EOFError:
            break
    print("\033[31mProcessing...\033[0m\n")  # Red color escape sequence
    return '\n'.join(lines)

def prepare_messages_for_api(messages):
    # Remove 'timestamp' field before sending to the API
    return [{"role": msg["role"], "content": msg["content"]} for msg in messages]

def load_file(filename):
    if os.path.exists(filename):
        try:
            messages = load_from_file(filename)
            original_messages = json.dumps(messages)  # Update original state after loading
            print(f"Context loaded from {filename}.")
            return filename, messages, original_messages
        except Exception as e:
            print(f"Error loading file: {e}")
    else:
        print("File does not exist.")

def check_load_file():
    if "--load" in sys.argv:
        load_file_index = sys.argv.index("--load") + 1
        if load_file_index < len(sys.argv):
            filename = sys.argv[load_file_index]
            if os.path.exists(filename):
                try:
                    return load_file(filename)
                except Exception as e:
                    print(f"Error loading file: {e}")
            else:
                print("File does not exist.")
    return "", [], None

# If it's a valid model, return the model name. Otherwise, return False
def validate_model(model):
    supported_models = {
        "gpt3.5": "gpt-3.5-turbo-0125",
        "gpt4": "gpt-4-0613"
    }
    for key, value in supported_models.items():
        if model == key:
            return value
    return False

# If we specify a model in the command line, use that. Otherwise, use gpt3.5.
# For unsupported models, exit the program.
def check_model():
    if "--model" in sys.argv:
        model_index = sys.argv.index("--model") + 1
        if model_index < len(sys.argv):
            model = validate_model(sys.argv[model_index])
            if model:
                return model
            print(f"Unsupported model: {sys.argv[model_index]}")
            exit(1)
    return validate_model("gpt3.5")

def check_names():
    if "--names" in sys.argv:
        name_index = sys.argv.index("--names") + 1
        if name_index < len(sys.argv):
            names = sys.argv[name_index]

            # Names is a comma separated list of two names.  If there is only one,
            # we use that for the assistant, if there are two, we use the first for
            # the assistant and the second for the user.
            nameList = names.split(',')
            if len(nameList) == 1:
                return nameList[0], "User"
            elif len(nameList) == 2:
                return nameList[0], nameList[1]
            print("Invalid names list -- either 1 or 2 names separated by a comma for the assistant and user.")
            exit(1)
    return "Assistant", "User"

def help_message():
    print()
    print(f"  Usage: {os.path.basename(__file__)} [--load filename] [--model modelname] [--names name1,name2]")
    print()
    print("    --load filename: Load conversation context from a file (contains system prompt)")
    print("    --model modelname: Choose a model to use (gpt3.5 or gpt4)")
    print("    --names name1,name2: Choose names for the assistant and user")
    print()

if "--help" in sys.argv or "-h" in sys.argv:
    help_message()
    exit(0)

# Initialize the OpenAI client
client = OpenAI()

# If user did --load filename, we'll load the file. Otherwise, we'll ask them to choose a system prompt.
filename, messages, original_messages = check_load_file()

# If user did --model modelname, we'll use that model. Otherwise, we'll use gpt3.5.
model = check_model()

# if user did --names name1,name2, we'll use those names. Otherwise, we'll use the default names.
assistant_name, user_name = check_names()

# Track the time so we can store it with the messages.
timestamps = [get_timestamp()]

# Start an infinite loop to keep the conversation going
while True:
    user_input = get_multiline_input("\nEnter your command (type 'help' for options), or your conversation text:", user_name)

    if user_input.lower() == 'help':
        print("Commands:\n  'view' - See conversation context\n  'clear' - Start over the conversation\n  'save' - Save conversation context\n  'load' - Load conversation context\n  'quit' - Quit the program\n  'help' - Show this help message\n  Enter anything else to continue the conversation.")

    elif user_input.lower() == 'view':
        print_conversation(messages)

    elif user_input.lower() == 'clear':
        messages = [{"role": "system", "content": "You are a helpful assistant.", "timestamp": get_timestamp()}]
        timestamps = [get_timestamp()]
        print("Conversation context cleared. Starting over.")

    elif user_input.lower() == 'save':
        tmpOutputFilename = input("Enter filename to save the context (enter means current one): ")
        if tmpOutputFilename == "":
            tmpOutputFilename = filename
        save_to_file(messages, tmpOutputFilename)
        original_messages = json.dumps(messages)  # Update original state after saving
        print(f"Context saved to {tmpOutputFilename}.")

        # The filename is updated to the saved filename.
        filename = tmpOutputFilename

    elif user_input.lower() == 'load':
        tmpInputFilename = input("Enter filename to load the context: ")
        filename, messages, original_messages = load_file(tmpInputFilename)

    elif user_input.lower() == 'quit':
        if original_messages != json.dumps(messages):
            print("You have unsaved changes. Please save your context before quitting.")
        else:
            print("Goodbye!")
            break
    else:
        messages.append({"role": "user", "content": user_input, "timestamp": get_timestamp()})
        api_messages = prepare_messages_for_api(messages)

        # Calculate tokens
        total_chars = sum(len(msg['content']) for msg in api_messages)
        estimated_tokens = total_chars // 4  # Rough estimation
        print(f"Estimated tokens to be sent: {estimated_tokens}")

        # Ask user to press <ENTER> to confirm they want to send the message
        print(f"Press <ENTER> to send the message to the '{model}' assistant, or type 'cancel' to cancel.")
        confirm = input()
        if confirm.lower() == 'cancel':
            print("\033[91mMessage canceled.\033[0m")
            messages.pop()
            continue
        start_time = time.time()  # Start timing

        response = client.chat.completions.create(
            model=model,
            messages=api_messages
        )

        end_time = time.time()  # End timing

        print()
        dashes()
        response_time = end_time - start_time
        print(f"\033[1m\033[91mResponse time: {response_time:.2f} seconds\033[0m")

        assistant_response = response.choices[0].message.content
        print(f"\n\033[1m\033[92m{assistant_name}:\033[0m")
        print(wrap_text(assistant_response))
        messages.append({"role": "assistant", "content": assistant_response, "timestamp": get_timestamp()})
