#!/usr/bin/env python

import time
import textwrap
import json
import os
import sys
import glob
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from openai import OpenAI

# Constants for ANSI color codes
ANSI_RED = "\033[91m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"

def dashes() -> None:
    """Print 80 dashes for separation."""
    print(f"{ANSI_BOLD}{ANSI_RED}{'-' * 80}{ANSI_RESET}")

def wrap_text(text: str, width: int = 80) -> str:
    """Wrap text except inside code blocks."""
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

def print_conversation(messages: List[Dict[str, str]]) -> None:
    """Print the formatted conversation."""
    for message in messages:
        dashes()
        timestamp = message.get("timestamp", "->")
        formatted_text = wrap_text(message['content'])
        model = message.get("model", "unknown model")
        if message['role'] == "Assistant":
            print(f"{timestamp} {ANSI_BOLD}{ANSI_GREEN}{message['role'].title()({model})}{ANSI_RESET}:")
        else:
            print(f"{timestamp} {ANSI_BOLD}{ANSI_GREEN}{message['role'].title()}{ANSI_RESET}:")
        print(formatted_text)

def save_to_file(messages: List[Dict[str, str]], filename: str) -> None:
    """Save messages to a file."""
    with open(filename, 'w') as file:
        json.dump(messages, file, indent=2)

def load_from_file(filename: str) -> List[Dict[str, str]]:
    """Load messages from a file."""
    with open(filename, 'r') as file:
        return json.load(file)

def get_timestamp() -> str:
    """Return the current timestamp."""
    return datetime.now().strftime("%Y-%m-%d-%H:%M")

def get_multiline_input(prompt: str, user_name: str = "User") -> str:
    """Get multiline input from the user."""
    print(f"{ANSI_YELLOW}{prompt}{ANSI_RESET}")
    print(f"{ANSI_BOLD}{ANSI_GREEN}{user_name}->{model}{ANSI_RESET}, enter your text, then finish with Ctrl-D on a blank line.\n")
    lines = []
    while True:
        try:
            line = input()
            # Check if line contains only Ctrl-D
            if line == "\x04":
                break
            lines.append(line)
        except EOFError:
            break
    print(f"{ANSI_RED}Processing...{ANSI_RESET}\n")
    return '\n'.join(lines)

def prepare_messages_for_api(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
    """Prepare messages for the API by removing timestamps."""
    return [{"role": msg["role"], "content": msg["content"]} for msg in messages]

def load_file(filename: str) -> Tuple[str, List[Dict[str, str]], Optional[str] ]:
    """
    Load messages from a file.

    Args:
    - filename (str): The name of the file to load.

    Returns:
    - Tuple containing the filename, messages, and a string representation of the original messages.
    """
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

def check_load_file() -> Tuple[str, List[Dict[str, str]], Optional[str]]:
    """
    Check if a file should be loaded based on command line arguments.

    Returns:
    - Tuple containing the filename, messages, and a string representation of the original messages.
    """
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

def validate_model(model: str) -> Optional[str]:
    """Validate if the provided model is supported.

    Args:
    - model (str): The model name to validate.

    Returns:
    - Optional[str]: The internal model name if supported, None otherwise.
    """

    supported_models = {
        "gpt3.5": "gpt-3.5-turbo-0125",
        "gpt4": "gpt-4-0613"
    }
    return supported_models.get(model)

def check_model() -> str:
    """Check and return the model specified in command line arguments.
       For unsupported models, exit the program.

    Returns:
    - str: The validated model name to be used.
    """
    if "--model" in sys.argv:
        model_index = sys.argv.index("--model") + 1
        if model_index < len(sys.argv):
            model = validate_model(sys.argv[model_index])
            if model:
                return model
            print(f"Unsupported model: {sys.argv[model_index]}")
            exit(1)
    return validate_model("gpt3.5")

def check_names() -> Tuple[str, str]:
    """Check and return the names specified in command line arguments.

    Returns:
    - Tuple[str, str]: Names for the assistant and user.
    """
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

def help_message() -> None:
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
        print("Commands:\n  'view' - See conversation context\n  'clear' - Start over the conversation\n  'save' - Save conversation context\n  'load' - Load conversation context\n  'model' - Choose a different model\n  'quit' - Quit the program\n  'help' - Show this help message\n  Enter anything else to continue the conversation.")

    elif user_input.lower() == 'model':
        model = input("Enter the model name (gpt3.5 or gpt4): ")
        model = validate_model(model)
        if not model:
            print("Unsupported model. Please choose gpt3.5 or gpt4.")
        else:
            print(f"Model changed to {model}.")
            
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
        messages.append({"role": "assistant",
                         "content": assistant_response,
                         "timestamp": get_timestamp(),
                         "model": model})
