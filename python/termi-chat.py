#!/usr/bin/env python

import time
import textwrap
import json
import os
import sys
import glob
import requests
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from openai import OpenAI
from spinner import Spinner
from simple_term_menu import TerminalMenu

# Constants for ANSI color codes
ANSI_RED = "\033[91m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"

# When you add a new model, add it to the SUPPORTED_MODELS dictionary
# and add a model family to the MODEL_FAMILIES dictionary.
SUPPORTED_MODELS = {
    # 16K context, optimized for dialog
    # $0.0005/1K tokens-in, $0.0015/1K tokens-out
    "gpt3.5": "gpt-3.5-turbo-0125",
    "gpt4": "gpt-4-0613",

    # 4K context using whatever is running on the text-generation-webui
    "Cassie": "Cassie",
    "Assistant": "Assistant"
}
MODEL_FAMILIES = {
    "gpt3.5": "openai",
    "gpt4": "openai",
    "Cassie": "textgeneration-webui",
    "Assistant": "textgeneration-webui"
}

MODEL_LIST = ", ".join(SUPPORTED_MODELS.keys())
DEFAULT_MODEL = "gpt3.5"

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

def print_message(index: int, message: str) -> None:
    """Print the messages."""
    dashes()
    timestamp = message.get("timestamp", "->")
    formatted_text = wrap_text(message['content'])
    model = message.get("model", "unknown model")
    if message['role'] == "Assistant":
        print(f"[{index}] {timestamp} {ANSI_BOLD}{ANSI_GREEN}{message['role'].title()({model})}{ANSI_RESET}:")
    else:
        print(f"[{index}] {timestamp} {ANSI_BOLD}{ANSI_GREEN}{message['role'].title()}{ANSI_RESET}:")
    print(formatted_text)

def print_conversation(messages: List[Dict[str, str]], max_context: int) -> None:
    """Print the formatted conversation.
       We will always keep message[0] which contains the system prompt."""
    if len(messages) < 1:
        print("No conversation context to display.")
        return
    print(f"Length of messages: {len(messages)}")
    print_message(0, messages[0])
    print("here")
    if max_context < len(messages):
        rest_of_messages = messages[-max_context:]
    else:
        rest_of_messages = messages[1:]
    for index, message in enumerate(rest_of_messages):
        print_message(index + 1, message)

def save_to_file(loaded_filename, messages: List[Dict[str, str]], filename: str) -> None:
    """Save messages to a file.
       The loaded_filename is the filename passed in from the --load option; we will
       use the directory from the as the place to save the file"""
    if loaded_filename:
        directory = os.path.dirname(loaded_filename)
        filename = os.path.join(directory, filename)
    else:
        filename = os.path.join("/termi-chats", filename)

    print(f"Saving conversation context to {filename}")
    with open(filename, 'w') as file:
        json.dump(messages, file, indent=2)

def load_from_file(filename: str) -> List[Dict[str, str]]:
    """Load messages from a file."""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except Exception as e:
        # It's debatable if we want to exit here or let the user continue
        # with an empty context.  For now, we'll exit.
        print(f"An error occurred while loading messages from file {filename}: {e}")
        exit(1)

def get_timestamp() -> str:
    """Return the current timestamp."""
    return datetime.now().strftime("%Y-%m-%d-%H:%M")

def get_multiline_input(model: str, max_context: int, user_name: str, prompt: str) -> str:
    """Get multiline input from the user."""
    print(f"{ANSI_YELLOW}{prompt}{ANSI_RESET}")
    print(f"{ANSI_BOLD}{ANSI_GREEN}{user_name}->{model}(ctx={max_context}){ANSI_RESET}, enter your text, finish with Ctrl-D on a blank line (no input = menu)\n")
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

def prepare_messages_for_api(messages: List[Dict[str, str]], max_context: int) -> List[Dict[str, str]]:
    """Prepare messages for the API by extracting only what the api needs
    and limit messages to the first message (the system prompot) plus the
    last n messages where n is max_context.  Remember a message is a
    role/context pair where role can be either assistant or user"""

    # Limit messages to the first message plus the last n=max_context messages
    return [{"role": msg["role"], "content": msg["content"]} for msg in [messages[0]] + messages[-max_context:]]

def load_file(filename: str) -> Tuple[str, List[Dict[str, str]], Optional[str] ]:
    """
    Load messages from a file.
    Our caller already checked that the file exists.

    Args:
    - filename (str): The name of the file to load.

    Returns:
    - Tuple containing the filename, messages, and a string representation of the original messages.
    """
    try:
        messages = load_from_file(filename)
        original_messages = json.dumps(messages)  # Update original state after loading
        num_messages = len(messages)
        print(f"Context loaded from {filename}.")
        print(f"Loaded {num_messages} {'message' if num_messages == 1 else 'messages'}")
        return filename, messages, original_messages
    except Exception as e:
        print(f"Error loading file: {e}")

def check_max_context() -> int:
    """Check and return the max context specified in command line arguments.
       If you have a conversation with a large number of back and forth messages,
       the context gets rather big.  You can limit the context to the last n
       messages (a lot of the time, the most recent messages are the most
       relevant anyway).

    Returns:
    - int: The max context to be used.
    """
    if "--max" in sys.argv:
        max_context_index = sys.argv.index("--max") + 1
        if max_context_index < len(sys.argv):
            try:
                return int(sys.argv[max_context_index])
            except ValueError:
                print("Invalid max context value. Please enter an integer.")
                exit(1)

    # Default max context
    return 100

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

            # if filename is a directory, glob the directory for *.json files, sort,
            # and present a menu to the user to choose a file to load.
            if os.path.isdir(filename):
                files = glob.glob(os.path.join(filename, "*.json"))
                files = sorted([os.path.basename(file) for file in files], key=str.lower)
                if len(files) == 0:
                    print(f"No JSON files found in {filename}")
                    exit(1)
                else:
                    # Given the menu so user can choose a file to load.
                    options = files
                    terminal_menu = TerminalMenu(options)
                    selected_option = terminal_menu.show()
                    print(f"Selected option: {selected_option}")
                    if selected_option is None:
                        print("No file selected. Exiting.")
                        exit(0)
                    else:
                        filename = os.path.join(filename, files[selected_option])
            else:
                filename = files[0]
            if os.path.exists(filename):
                try:
                    return load_file(filename)
                except Exception as e:
                    print(f"Error loading file: {e}")
            else:
                print("File does not exist.")
    return "", [], None

def validate_model(model: str) -> Tuple[str, str]:
    """Validate if the provided model is supported.

    Args:
    - model (str): The model name to validate.

    Returns:
    - Optional[str]: The internal model name if supported, None otherwise; the model family if supported, None otherwise.
    - Optional[str]: The model family if supported, None otherwise.
    """
    return SUPPORTED_MODELS.get(model), MODEL_FAMILIES.get(model)

def check_model() -> Tuple[str, str]:
    """Check and return the model specified in command line arguments.
       For unsupported models, exit the program.

    Returns:
    - str: The validated model name to be used.
    """
    if "--model" in sys.argv:
        model_index = sys.argv.index("--model") + 1
        if model_index < len(sys.argv):
            model, family = validate_model(sys.argv[model_index])
            if model:
                return model, family
            print(f"Unsupported model: {sys.argv[model_index]}")
            exit(1)
    return validate_model(DEFAULT_MODEL)

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
    print(f"    --load filename: Load conversation context from a file (contains system prompt)")
    print(f"    --model modelname: Choose a model to use ({MODEL_LIST})")
    print(f"    --names name1,name2: Choose names for the assistant and user")
    print(f"    --max number: set max previous messages to use for context (this uses less tokens)")
    print()

if "--help" in sys.argv or "-h" in sys.argv:
    help_message()
    exit(0)

def send_message_to_openai(client: OpenAI, model: str, api_messages: List[Dict[str, str]]) -> str:
    """Send a message to the OpenAI API and return the response.
        Returns a response from the model once complete (or error (e.g., timeout))"""

    spinner = Spinner()

    def send_request():
        nonlocal spinner
        try:
            spinner.set_response(client.chat.completions.create(
                model=model,
                messages=api_messages
            ))
        except Exception as e:
            print(f"Error: {e}")

    spinner.start(send_request)

    # Handle the response after spinner finishes
    response = spinner.response

    if response is None:
        print(f"{ANSI_BOLD}{ANSI_RED}\nTimeout condition: Request took too long to complete{ANSI_RESET}")

    sys.stdout.flush()

    # OpenAI has to status code -- so if we get a response, we assume 200 OK.
    # See https://community.openai.com/t/http-status-for-chat-completion/541491
    if response:
        return response.choices[0].message.content
    else:
        print(f"Request failed with unknown status code")
        return f"{ANSI_BOLD}{ANSI_RED}Error talking to model {model}: {str(response)}{ANSI_RESET}"

def send_message_to_local_TGWI(client: OpenAI, model: str, api_messages: List[Dict[str, str]]) -> str:
    """Send a message to the text-generation-webui in the background and return immediately.
        Returns a response from the model once complete (or error (e.g., timeout))"""
    url = "http://192.168.1.52:5089/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    data = {
        "messages": api_messages,
        "mode": "chat",
        "character": model,
    }
    spinner = Spinner()

    def post_request():
        nonlocal spinner
        try:
            spinner.set_response(requests.post(url, json=data, headers=headers))
        except Exception as e:
            print(f"Error: {e}")

    spinner.start(post_request)

    # Handle the response after spinner finishes
    response = spinner.response

    if response is None:
        print(f"{ANSI_BOLD}{ANSI_RED}\nTimeout condition: Request took too long to complete{ANSI_RESET}")

    if response and response.status_code == 200:
        sys.stdout.flush()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        sys.stdout.flush()
        if response:
            print(f"Request failed with status code {response.status_code}: {response.text}")
        return f"{ANSI_BOLD}{ANSI_RED}Error talking to model {model}: {str(response)}{ANSI_RESET}"

menu_items = {
    "clear - Start over the conversation (retain the System prompt)": "clear",
    "load  - Load conversation context": "load",
    "max   - Set max back context": "max",
    "model - Choose a different model": "model",
    "names - Choose different names for the assistant and user": "names",
    "save  - Save conversation context": "save",
    "view  - See conversation context": "view",
    "quit  - Quit the program": "quit",
    "exit  - Quit without saving": "exit"
}

model_menu_items = {
    "GPT-3.5": "gpt3.5",
    "GPT-4": "gpt4",
    "Cassie (local)": "Cassie",
    "Assistant (local)": "Assistant"
}

# We only need the OpenAI client if we are using an OpenAI model
# This makes it so you don't need an API key if you are using a
# local model.
openaiClient = None

# If user did --load filename, we'll load the file. Otherwise, we'll ask them to choose a system prompt.
filename, messages, original_messages = check_load_file()

# If user did --model modelname, we'll use that model. Otherwise, we'll use DEFAULT_MODEL.
model, family = check_model()

# if user did --names name1,name2, we'll use those names. Otherwise, we'll use the default names.
assistant_name, user_name = check_names()

# if user did --max, we'll use that max context. Otherwise, we'll use the default max context.
max_context = check_max_context()

# Track the time so we can store it with the messages.
timestamps = [get_timestamp()]

# Start an infinite loop to keep the conversation going
while True:
    user_input = get_multiline_input(model, max_context, user_name, "\nEnter your command (type 'help' for options), or your conversation text:")

    if user_input.lower() == 'm' or user_input.lower() == 'menu' or user_input.lower() == '':
        options = list(menu_items.keys())
        terminal_menu = TerminalMenu(options)
        selected_option = terminal_menu.show()
        if selected_option is None:
            # Escape was pressed so do nothing.
            continue
        user_input = menu_items[options[selected_option]]

    if user_input.lower() == 'model':
        options = list(model_menu_items.keys())
        terminal_menu = TerminalMenu(options)
        selected_option = terminal_menu.show()
        if selected_option is None:
            # Escape was pressed so do nothing.
            print("Model not changed.")
            continue
        model = model_menu_items[options[selected_option]]
        model, family = validate_model(model)
        print(f"Model changed to {model}.")

    elif user_input.lower() == 'names':
        tmp_input = input(f"Enter the assistant name (blank = no change, default = {assistant_name}): ")
        if len(tmp_input) > 0:
            assistant_name = tmp_input
            print(f"Assistant name changed to {assistant_name}.")
        else:
            print(f"Assistant name not changed.")
        tmp_input = input(f"Enter the user name (blank = no change, default = {user_name}): ")
        if len(tmp_input) > 0:
            user_name = tmp_input
            print(f"User name changed to {user_name}.")
        else:
            print(f"User name not changed.")
        continue

    elif user_input.lower() == 'max':
        # We'll need to increase context number as we progress int the conversation
        # and then the max will be shown.  For now, just try to do some rudimentary
        # checking to make sure the number is valid.
        if len(messages) < 2:
            print("No conversation context so max context cannot be changed.")
            continue
        tmp_input = input(f"Enter the max context to use (blank = no change, max = {len(messages)-1}): ")
        if len(tmp_input) > 0:
            try:
                max_context = int(tmp_input)
                if max_context >= len(messages):
                    print(f"Invalid max context. Please enter a value less than {len(messages)}")
                    continue
            except ValueError:
                print("Invalid max context. Please enter a valid integer.")
                continue
            print(f"Max context changed to {max_context}.")
        else:
            print(f"Max context not changed.")

    elif user_input.lower() == 'view':
        print_conversation(messages, max_context)

    elif user_input.lower() == 'clear':
        # Just keep the system message and clear the rest.
        messages = [{"role": "system", "content": messages[0]["content"], "timestamp": get_timestamp()}]
        timestamps = [get_timestamp()]
        print("Conversation context cleared. Starting over.")

    elif user_input.lower() == 'save':
        tmpOutputFilename = input("Enter filename to save the context (enter means current one): ")
        if tmpOutputFilename == "":
            tmpOutputFilename = filename
        save_to_file(filename, messages, tmpOutputFilename)
        original_messages = json.dumps(messages)  # Update original state after saving
        print(f"Context saved to {tmpOutputFilename}.")

        # The filename is updated to the saved filename.
        filename = tmpOutputFilename

    elif user_input.lower() == 'load':
        filename, messages, original_messages = check_load_file()

    elif user_input.lower() == 'quit':
        if original_messages != json.dumps(messages):
            print("You have unsaved changes. Please save your context before quitting.")
        else:
            print("Quitting.\n")
            break

    elif user_input.lower() == 'exit':
        print("Exiting without saving!\n")
        break
    else:
        messages.append({"role": "user", "content": user_input, "timestamp": get_timestamp()})
        api_messages = prepare_messages_for_api(messages, max_context)

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

        if family == "openai":
            if openaiClient is None:
                # Initialize the OpenAI client
                openaiClient = OpenAI()
            assistant_response = send_message_to_openai(openaiClient, model, api_messages)
        elif family == "textgeneration-webui":
            assistant_response = send_message_to_local_TGWI(openaiClient, model, api_messages)
        else:
            print(f"Unsupported model family: {family}")
            exit(1)

        end_time = time.time()  # End timing

        print()
        dashes()
        response_time = end_time - start_time
        print(f"\033[1m\033[91mResponse time: {response_time:.2f} seconds\033[0m")

        print(f"\n\033[1m\033[92m{assistant_name}:\033[0m")
        print(wrap_text(assistant_response))
        messages.append({"role": "assistant",
                         "content": assistant_response,
                         "timestamp": get_timestamp(),
                         "model": model})
