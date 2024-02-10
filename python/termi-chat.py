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
from tiktoken import encoding_for_model

# Used for counting tokens
TOKEN_ENCODING = encoding_for_model("text-davinci-003")

# Constants for ANSI color codes
ANSI_LIGHTBLUE = "\033[94m"
ANSI_RED = "\033[91m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"

# When you add a new model, add it to the MODEL_INFO dictionary.
# The first model is the default.
MODEL_INFO = {
    "gpt3.5": {
        # 16K context, optimized for dialog
        "model_api_name": "gpt-3.5-turbo-0125",
        "model_family": "openai",
        "cost_input": 0.0005,
        "cost_output": 0.0015
    },
    "gpt4": {
        "model_api_name": "gpt-4-0613",
        "model_family": "openai",
        "cost_input": 0.01,
        "cost_output": 0.03
    },
    "Cassie": {
        # 4K context using whatever is running on the text-generation-webui
        "model_api_name": "Cassie",
        "model_family": "text-generation-webui",
        "cost_input": 0.01,
        "cost_output": 0.03
    },
    "Assistant": {
        # 4K context using whatever is running on the text-generation-webui
        "model_api_name": "Assistant",
        "model_family": "text-generation-webui",
        "cost_input": 0.0,
        "cost_output": 0.0
    }
}

MODEL_LIST = ", ".join(MODEL_INFO.keys())

# The first one is the default.
DEFAULT_MODEL = MODEL_LIST[0]

# The total accumulated cost for the conversation(s)
_total_cost = 0

def _get_model_cost_values(model_api_name: str) -> Tuple[float, float]:
    """Get the cost values for any model_api_name as a pair of cost/1k tokens for input and output.
       If the model is not supported, we will use high cost estimates."""

    # Search for the model short name with the matching model_api_name.
    for model, info in MODEL_INFO.items():
        if info["model_api_name"] == model_api_name:
            break
    else:
        print(f"Unsupported model: {model}; using high cost estimates")
        return 0.99, 0.99

    return MODEL_INFO[model]["cost_input"], MODEL_INFO[model]["cost_output"]

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

def get_spent(amount: float) -> str:
    """Return a string that shows the amount spent so far.
       If the amount is zero, it is green, otherwise it is red."""
    if amount == 0.0:
        return f"{ANSI_GREEN}${amount:.4f}{ANSI_RESET}"
    else:
        return f"{ANSI_RED}${amount:.4f}{ANSI_RESET}"

def get_multiline_input(model: str, max_context: int, user_name: str, prompt: str) -> str:
    """Get multiline input from the user."""
    print(f"{ANSI_YELLOW}{prompt}{ANSI_RESET}")
    print(f"{ANSI_BOLD}{ANSI_GREEN}{user_name}->{model}(ctx={max_context},spent={ANSI_RESET}{get_spent(_total_cost)}{ANSI_BOLD}{ANSI_GREEN}){ANSI_RESET}, enter some (multi-line) text, finish with Ctrl-D on a blank line (Ctrl-D for menu)\n")
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

def load_json_file(filename: str) -> Tuple[str, List[Dict[str, str]], str]:
    """
    Load messages from a file.
    Our caller already checked that the file exists.

    Args:
    - filename (str): The name of the file to load.

    Returns:
    - Tuple containing
    - str: the filename
    - List of Dict[str,str]: messages
    - str: flat string representatino of messages (used to track changes to the original
      messages read from the file)
    """
    try:
        messages = load_from_file(filename)
        original_messages = json.dumps(messages)
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

def get_file_or_dir_from_cli() -> str:
    """Check and return the file or directory specified in command line arguments.

    Returns:
    - str: The file or directory specified by the --load option; if nothing specified, default
      to the current working directory.
    """
    if "--load" in sys.argv:
        load_file_index = sys.argv.index("--load") + 1
        if load_file_index < len(sys.argv):
            return sys.argv[load_file_index]
    return os.getcwd()

def check_load_file(filename: str) -> Tuple[str, List[Dict[str, str]], str]:
    """
    Given a filename, determine if it's a directory or a file and load the file.
    If it's a directory, we'll glob the directory and make a menu.

    Returns:
    - Tuple containing
      - str: the filename
      - List of Dict[str,str]: messages
      - str: flat string representatino of messages (used to track changes to the original
        messages read from the file)
    """
    # if filename is a directory, glob the directory for *.json files, sort,
    # and present a menu to the user to choose a file to load.
    if os.path.isdir(filename):
        files = glob.glob(os.path.join(filename, "*.json"))
        files = sorted([os.path.basename(file) for file in files], key=str.lower)
        if len(files) == 0:
            print(f"No JSON files found in {filename}; use --load <aDir> or --load <aJsonFile> to specify a file or directory.")
            exit(1)
        else:
            # Give the menu so user can choose a file to load.
            options = files
            terminal_menu = TerminalMenu(options)
            selected_option = terminal_menu.show()
            if selected_option is None:
                print("No file selected. Exiting.")
                exit(0)
            else:
                filename = os.path.join(filename, files[selected_option])
    if os.path.exists(filename):
        try:
            return load_json_file(filename)
        except Exception as e:
            print(f"Error loading file: {e}")
    else:
        print("File does not exist.")
    return "", [], None

def inform_model_cost(model: str) -> None:
    """Print out how much a model costs to use."""
    print(f"Model set to {model}.")
    tmp_input_cost, tmp_output_cost = _get_model_cost_values(model_api_name)
    if tmp_input_cost > 0.0 or tmp_output_cost > 0.0:
        print(f"{ANSI_RED}{ANSI_BOLD}Cost: ${tmp_input_cost:.4f}/1k input tokens, ${tmp_output_cost:.4f}/1k output tokens{ANSI_RESET}")
    else:
        print(f"{ANSI_GREEN}{ANSI_BOLD}Cost: Free!{ANSI_RESET}")

def get_model_api_and_family(model: str) -> Tuple[str, str, str]:
    """Given a model "short" name, validate the model and return the model's api name and family.

    Args:
    - model (str): The "short" version of the model to validate; see the keys of MODEL_INFO.

    Returns:
    - The model's "short" name.
    - The model's api name if supported, None otherwise.
    - The model family if supported, None otherwise.
    """
    return model, MODEL_INFO.get(model)["model_api_name"], MODEL_INFO.get(model)["model_family"]

def get_model_from_cli() -> str:
    """Check and return the model (the "short" name) specified in command line arguments.
       If the model is not specified, return the default model.
       For unsupported models, exit the program

    Returns:
    - str: the model short anme as passed in the cli
    """
    if "--model" in sys.argv:
        model_index = sys.argv.index("--model") + 1
        model = sys.argv[model_index]
        if model_index < len(sys.argv):
            unused, model_api_name, family = get_model_api_and_family(model)
            if model_api_name:
                return model
            print(f"Unsupported model: {model}; valid modes: {MODEL_LIST}")
            exit(1)
    return DEFAULT_MODEL

def check_cli_names(model: str) -> Tuple[str, str]:
    """Given the model "short" name, check and return the names specified in
       command line (--names) arguments.

    Returns:
    - Tuple[str, str]: Names for the assistant and user.
    """
    # Match the ChatGPT UI for names regardless of what the user specified for --names
    if model == "gpt3.5" or model == "gpt4":
        return "ChatGPT", "You"
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

def send_message_to_openai(client: OpenAI, model_api_name: str, api_messages: List[Dict[str, str]]) -> Tuple[str, float]:
    """Send a message to the OpenAI API and return the response.
        Returns a response from the model once complete (or error (e.g., timeout))
        and the cost of the request."""

    spinner = Spinner()

    def send_request():
        nonlocal spinner
        try:
            spinner.set_response(client.chat.completions.create(
                model=model_api_name,
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
        cost_per_input_1k_tokens, cost_per_output_1k_tokens = _get_model_cost_values(model_api_name)
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        total_tokens = input_tokens + output_tokens
        cost_for_input = cost_per_input_1k_tokens * input_tokens / 1000
        cost_for_output = cost_per_output_1k_tokens * output_tokens / 1000
        total_for_both = cost_for_input + cost_for_output

        global _total_cost
        _total_cost += total_for_both
        print(f"\nCost: ${cost_for_input:.4f} for input, ${cost_for_output:.4f} for output, total: ${total_for_both:.4f}")
        return response.choices[0].message.content, total_for_both
    else:
        print(f"\nRequest failed with unknown status code")
        return f"{ANSI_BOLD}{ANSI_RED}Error talking to model {model_api_name}: {str(response)}{ANSI_RESET}", 0.0

def send_message_to_local_TGW(client: OpenAI, model_api_name: str, api_messages: List[Dict[str, str]]) -> Tuple[str, float]:
    """Send a message to the text-generation-webui in the background and return immediately.
        Returns a response from the model once complete (or error (e.g., timeout))
        and the cost of the request."""
    url = "http://192.168.1.52:5089/v1/chat/completions"
    headers = {"Content-Type": "application/json"}

    data = {
        "messages": api_messages,
        "mode": "chat",
        "character": model_api_name,
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


        cost_per_input_1k_tokens, cost_per_output_1k_tokens = _get_model_cost_values(model_api_name)
        input_tokens = get_estimated_tokens(api_messages)
        output_tokens = get_estimated_tokens_for_message(result["choices"][0]["message"]["content"])
        total_tokens = input_tokens + output_tokens
        cost_for_input = cost_per_input_1k_tokens * input_tokens / 1000
        cost_for_output = cost_per_output_1k_tokens * output_tokens / 1000
        total_for_both = cost_for_input + cost_for_output

        global _total_cost
        _total_cost += total_for_both
        print(f"\nCost: ${cost_for_input:.4f} for input, ${cost_for_output:.4f} for output, total: ${total_for_both:.4f}")
        return result["choices"][0]["message"]["content"], total_for_both
    else:
        sys.stdout.flush()
        if response:
            print(f"Request failed with status code {response.status_code}: {response.text}")
        return f"{ANSI_BOLD}{ANSI_RED}Error talking to model {model_api_name}: {str(response)}{ANSI_RESET}", 0.0

def get_estimated_tokens(api_messages: List[Dict[str, str]]) -> int:
    tokens = sum(len(TOKEN_ENCODING.encode(messages['content'])) for messages in api_messages)
    return tokens

def get_estimated_tokens_for_message(message: str) -> int:
    return len(TOKEN_ENCODING.encode(message))

menu_items = {
    "[c] clear   - Start over the conversation (retain the System prompt)": "clear",
    "[l] load    - Load conversation context": "load",
    "[m] max     - Set max back context": "max",
    "[o] model   - Choose a different model": "model",
    "[n] names   - Choose different names for the assistant and user": "names",
    "[s] save    - Save conversation context": "save",
    "[r] resend  - Resend the current context (with no new input)": "resend",
    "[v] view    - See conversation context": "view",
    "[q] quit    - Quit the program": "quit",
    "[e] exit    - Quit without saving": "exit"
}

# The second one is the model "short" name which should match the keys in MODEL_INFO.
model_menu_items = {
    "[3] GPT-3.5": "gpt3.5",
    "[4] GPT-4": "gpt4",
    "[c] Cassie (local)": "Cassie",
    "[a] Assistant (local)": "Assistant"
}

# We only need the OpenAI client if we are using an OpenAI model
# This makes it so you don't need an API key if you are using a
# local model.
openaiClient = None

# If user did --load filename, we'll load the file. Otherwise, we'll ask them to choose a system prompt.
file_or_dir_from_cli = get_file_or_dir_from_cli()

# original_messages is used to track if there were changes to the original messages.
filename, messages, original_messages = check_load_file(file_or_dir_from_cli)

# If user did --model modelname, we'll use that model. Otherwise, we'll use DEFAULT_MODEL.
model = get_model_from_cli()
model, model_api_name, family = get_model_api_and_family(model)
inform_model_cost(model_api_name)

# if user did --names name1,name2, we'll use those names. Otherwise, we'll use the default names.
assistant_name, user_name = check_cli_names(model)

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
        unused, model_api_name, family = get_model_api_and_family(model)
        inform_model_cost(model_api_name)
        assistant_name, user_name = check_cli_names(model)

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
        filename, messages, original_messages = check_load_file(file_or_dir_from_cli)

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

        if user_input.lower() == 'resend':
            # If the user sends a message, we'll send it to the assistant and then print the response.
            # We'll also track the time it takes to get the response.
            if len(messages) < 2:
                print("No conversation context to send to the assistant.")
                continue
            print(f"Sending {ANSI_LIGHTBLUE}unchanged{ANSI_RESET} conversation context to {model} assistant...")
        else:
            # Add the user's input to the messages
            print(f"Sending conversation context to {model} assistant...")
            messages.append({"role": "user", "content": user_input, "timestamp": get_timestamp()})

        api_messages = prepare_messages_for_api(messages, max_context)

        # Calculate tokens
        estimated_tokens = get_estimated_tokens(api_messages)
        print(f"Estimated tokens to be sent: {estimated_tokens}")

        # Ask user to press <ENTER> to confirm they want to send the message
        options = [ f"Send to '{model}' assistant", "Cancel" ]
        terminal_menu = TerminalMenu(options)
        selected_option = terminal_menu.show()
        if selected_option is None:
            # Escape was pressed so do nothing.
            confirm = 'cancel'
        else:
            confirm = options[selected_option]
        if confirm.lower() == 'cancel':
            print("\033[91mMessage canceled.\033[0m")
            messages.pop()
            continue
        start_time = time.time()  # Start timing

        if family == "openai":
            if openaiClient is None:
                # Initialize the OpenAI client
                openaiClient = OpenAI()
            assistant_response, tmp_cost = send_message_to_openai(openaiClient, model_api_name, api_messages)
        elif family == "text-generation-webui":
            assistant_response, tmp_cost = send_message_to_local_TGW(openaiClient, model_api_name, api_messages)
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
                 "model": model,
                 "response_seconds": round(response_time, 2),
                 "cost_dollars": tmp_cost})
