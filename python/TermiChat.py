import time
import json
import os
import sys
import glob
import requests
import readline
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from openai import OpenAI
from spinner import Spinner
from ModelInfo import MODEL_INFO
from simple_term_menu import TerminalMenu
from tiktoken import encoding_for_model
from utils import get_model_info, marker_message, warn_message, info_message, dashes, wrap_text, ANSI_BOLD, ANSI_YELLOW, ANSI_GREEN, ANSI_LIGHTBLUE, ANSI_RED, ANSI_RESET

# Used for counting tokens
TOKEN_ENCODING = encoding_for_model("text-davinci-003")

# When you add a new model, add it to the MODEL_INFO dictionary.
# See https://openai.com/pricing#language-models for pricing.
# The first model is the default.

# Used for things that need all models.
MODEL_LIST_AS_STRING = ", ".join(MODEL_INFO.keys())

# Used for iteration.
MODEL_LIST = [model for model in MODEL_INFO.keys()]

# The first one is the default.
DEFAULT_MODEL = MODEL_LIST[0]

DEFAULT_TERMI_CHAT_DIRNAME = "termi-chats"

MENU_ITEMS = {
    "[c] clear   - Start over the conversation (retain the System prompt)": "clear",
    "[l] load    - Load conversation context": "load",
    "[m] max     - Set max back context": "max",
    "[o] model   - Choose a different model": "model",
    "[i] info    - Show model info": "info",
    "[n] names   - Choose different names for the assistant and user": "names",
    "[s] save    - Save conversation context": "save",
    "[r] resend  - Resend the current context (with no new input)": "resend",
    "[v] view    - See conversation context": "view",
    "[q] quit    - Quit the program": "quit",
    "[x] exit    - Quit without saving": "exit"
}

# The second one is the model "short" name which should match the keys in MODEL_INFO.
# MODEL_MENU_ITEMS = {
#     "[3] GPT-3.5": "gpt3.5",
#     "[4] GPT-4": "gpt4",
#     "[c] Cassie (local)": "Cassie",
#     "[a] Assistant (local)": "Assistant"
# }

# Set MODEL_MENU_ITEMS to a dict that maps MODEL_INFO keys to model_api_name values.
MODEL_MENU_ITEMS = {model: MODEL_INFO[model]["model_api_name"] for model in MODEL_INFO}

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

    # return the current directory with the default dirname as
    # the default directory for saving conversation context.
    return os.path.join(os.getcwd(), DEFAULT_TERMI_CHAT_DIRNAME, "/")

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
        return model
    else:
        return DEFAULT_MODEL

def get_max_context_from_cli() -> int:
    """Check and return the max context specified in command line arguments.
    If you have a conversation with a large number of back and forth messages,
    the context gets rather big.  You can limit the context to the last n
    messages (a lot of the time, the most recent messages are the most
    relevant anyway).
    We always include message[0] which is the system prompt.

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

def help_message() -> None:
   print()
   print(f"  Usage: {os.path.basename(__file__)} [--load filename] [--model modelname] [--names name1,name2]")
   print()
   print(f"    --load filename: Load conversation context from a file (contains system prompt)")
   print(f"    --model modelname: Choose a model to use ({MODEL_LIST_AS_STRING})")
   print(f"    --names name1,name2: Choose names for the assistant and user")
   print(f"    --max number: set max previous messages to use for context (this uses less tokens)")
   print()

def get_names_from_cli(model_short_name: str) -> Tuple[str, str]:
    """Given the model "short" name, check and return the names specified in
       command line (--names) arguments.

    Returns:
    - Tuple[str, str]: Names for the assistant and user.
    """
    # Match the ChatGPT UI for names regardless of what the user specified for --names
    if model_short_name == "gpt3.5" or model_short_name == "gpt4":
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

class TermiChat:
    def __init__(self, name: str, model: str, max_context: int, assistant_name: str, user_name: str, file_or_dir_from_cli: str):
        self.name = name
        self.max_context = max_context
        self.assistant_name = assistant_name
        self.user_name = user_name

        # We only need the OpenAI client if we are using an OpenAI model
        # This makes it so you don't need an API key if you are using a
        # local model.
        self._openaiClient = None

        # Openrouter client is similar to OpenAI client.
        self._openrouterClient = None

        # The total accumulated cost for the conversation(s)
        self._total_cost = 0.0

        # Track the time so we can store it with the messages.
        self.timestamps = [self._get_timestamp()]

        # original_messages is used to track if there were changes to the original messages.
        self.filename, self.messages, self.original_messages = self.check_load_file(file_or_dir_from_cli)

        self.model, self.model_api_name, self.family = self._get_model_api_and_family(model)
        if self.filename == "":
            # TODO: later, we'll be ok with this (we can detect if this is the first message
            # later and if it is, we can call that the system prompt and not send it.
            print("No conversation context loaded -- aborting.")
            sys.exit(1)
        self._inform_model_cost(self.model_api_name)

    def _get_model_cost_values(self, model_api_name: str) -> Tuple[float, float]:
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

    def _print_message(self, index: int, message: Dict[str, str]) -> None:
        """Print a single message.  A message has evolved to be a dictionary with
           a role, content, and timestamp.  We will also print the model and the
           response time if it is an assistant message.  We will also print the
           cost of the message if it is an assistant message"""
        dashes()
        timestamp = message.get("timestamp", "->")
        formatted_text = wrap_text(message['content'])
        model = message.get("model", "unknown model")
        if message['role'] == "Assistant":
            print(f"[{index}] {timestamp} {ANSI_BOLD}{ANSI_GREEN}{message['role'].title()({model})}{ANSI_RESET}:")
        else:
            print(f"[{index}] {timestamp} {ANSI_BOLD}{ANSI_GREEN}{message['role'].title()}{ANSI_RESET}:")
        print(formatted_text)

    def _save_to_file(self, loaded_filename, messages: List[Dict[str, str]], filename: str) -> None:
        """Save messages to a file.

        Args:
        - str: loaded_filename is the filename passed in from the --load option; we will
          use the directory from the as the place to save the file
        - List of Dict[str,str]: messages is the messages to save to the file
        - str: filename is the filename to save the messages to (this could be different
          than the self.filename if the user specifies a different filename to save to)
        """
        if loaded_filename:
            # If we had a dir/filename passed, we'll use that for where to output the file.
            directory = os.path.dirname(loaded_filename)

            # If filename doesn't have a directory, we'll use the directory from the loaded_filename
            if not os.path.dirname(filename):
                filename = os.path.join(directory, filename)
        else:
            # The default dir for the files.
            filename = os.path.join("/", DEFAULT_TERMI_CHAT_DIRNAME, filename)

        print(f"Saving conversation context to {filename}")
        with open(filename, 'w') as file:
            json.dump(messages, file, indent=2)

    def _load_from_file(self, filename: str) -> List[Dict[str, str]]:
        """Load messages from a file.

        Args:
        - str: filename is the name of the file to load.

        Returns:
        - List of Dict[str,str]: messages were read from the file
        """
        try:
            with open(filename, 'r') as file:
                return json.load(file)
        except Exception as e:
            # It's debatable if we want to exit here or let the user continue
            # with an empty context.  For now, we'll exit.
            print(f"An error occurred while loading messages from file {filename}: {e}")
            exit(1)

    def _get_timestamp(self) -> str:
        """Return the current timestamp in a readable format so we can save when
        we send a message to the assistant."""
        return datetime.now().strftime("%Y-%m-%d-%H:%M")

    def _get_spent(self, amount: float) -> str:
        """Return a string that shows the amount spent so far.
           If the amount is zero, it is green, otherwise it is red."""
        if amount == 0.0:
            return f"{ANSI_GREEN}${amount:.4f}{ANSI_RESET}"
        else:
            return f"{ANSI_RED}${amount:.4f}{ANSI_RESET}"

    def _get_multiline_input(self, prompt: str) -> str:
        """Get multiline input from the user."""
        print(f"{ANSI_YELLOW}{prompt}{ANSI_RESET}")
        print(f"{ANSI_BOLD}{ANSI_GREEN}{self.user_name}->{self.model}(ctx={self.max_context},spent={ANSI_RESET}{self._get_spent(self._total_cost)}{ANSI_BOLD}{ANSI_GREEN}){ANSI_RESET}, enter some (multi-line) text, finish with Ctrl-D on a blank line (Ctrl-D for menu)\n")
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
        marker_message("Processing ...")
        return '\n'.join(lines)

    def _message_strip(self, message: Dict[str, str]) -> Dict[str, str]:
        """Strip off all but the role and content of the given message (message
        is a dict of [role:x, content:x, model:x, reponse_cost:x ...] where
        role and content are strings.  Our LLM only wants role and content."""
        return {"role": message["role"], "content": message["content"]}

    def _prepare_messages_for_api(self) -> List[Dict[str, str]]:
        """Prepare messages for the API by extracting only what the api needs
        and limit messages to the first message (the system prompt) plus the
        last n messages where n is max_context.  Remember a message is a
        role/context pair where role can be either assistant or user

        This is necessary because we add other data in the json and the api
        only wants role and content."""

        # Limit messages to the first message plus the last n=max_context messages

        if self.max_context == 0:
            return [self._message_strip(self.messages[0])]

        # calculate the 0th message plus messages 1-n upto max_context messages.
        ret_messasges = [self._message_strip(self.messages[0])]
        for i, message in enumerate(self.messages[1:]):
            if i < self.max_context:
                ret_messasges.append(self._message_strip(message))
        return ret_messasges

    def _load_json_file(self, filename: str) -> Tuple[str, List[Dict[str, str]], str]:
        """
        Load messages from a file.
        Our caller already checked that the file exists; this generic function
        does not modify any instance variables.

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
            tmp_messages = self._load_from_file(filename)
            tmp_original_messages = json.dumps(tmp_messages)
            num_messages = len(tmp_messages)
            print(f"Context loaded from {filename}.")
            print(f"Loaded {num_messages} {'message' if num_messages == 1 else 'messages'}")
            return filename, tmp_messages, tmp_original_messages
        except Exception as e:
            print(f"Error loading file: {e}")

    def check_load_file(self, filename_or_dir: str) -> Tuple[str, List[Dict[str, str]], str]:
        """
        Given a string for a filename_or_dir, determine if it's a directory or a file.
        If it's a directory, we'll glob the directory, make a menu, and let the user
        choose a file to load.  If it's a file, we'll load the file.  This generic
        function does not modify any instance variables.

        Returns:
        - Tuple containing
          - str: the filename
          - List of Dict[str,str]: messages
          - str: flat string representatino of messages (used to track changes to the original
            messages read from the file)
        """
        # if filename is a directory, glob the directory for *.json files, sort,
        # and present a menu to the user to choose a file to load.
        if os.path.isdir(filename_or_dir):
            files = glob.glob(os.path.join(filename_or_dir, "*.json"))
            files = sorted([os.path.basename(file) for file in files], key=str.lower)
            if len(files) == 0:
                print(f"No JSON files found in {filename_or_dir}; use --load <aDir> or --load <aJsonFile> to specify a file or directory.")
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
                    filename_or_dir = os.path.join(filename_or_dir, files[selected_option])
        if os.path.exists(filename_or_dir):
            try:
                return self._load_json_file(filename_or_dir)
            except Exception as e:
                print(f"Error loading file: {e}")
        else:
            print(f"{filename_or_dir}: file or directory does not exist.")
        return "", [], None

    def _inform_model_cost(self, model: str) -> None:
        """Print out how much a model costs to use."""
        print(f"Model set to {model}.")
        tmp_input_cost, tmp_output_cost = self._get_model_cost_values(self.model_api_name)
        if tmp_input_cost > 0.0 or tmp_output_cost > 0.0:
            warn_message(f"Cost: ${tmp_input_cost:.4f}/1k input tokens, ${tmp_output_cost:.4f}/1k output tokens")
        else:
            info_message(f"Cost: Free!")

    def _get_model_api_and_family(self, model_short_name: str) -> Tuple[str, str, str]:
        """Given a model "short" name, validate the model and return the model's api name and family.

        Args:
        - model (str): The "short" version of the model to validate; see the keys of MODEL_INFO.

        Returns:
        - The model's "short" name.
        - The model's api name if supported, None otherwise.
        - The model family if supported, None otherwise.
        """
        if ("openrouter.ai/" + model_short_name) in MODEL_LIST:
            # The shortnames had openrouter.ai prepended to them so we could
            # easily search for them when selecting the model.
            model_short_name = "openrouter.ai/" + model_short_name
            return model_short_name, MODEL_INFO.get(model_short_name)["model_api_name"], MODEL_INFO.get(model_short_name)["model_family"]
        if model_short_name not in MODEL_LIST:
            print(f"Unsupported model: {model_short_name}; valid modes: {MODEL_LIST_AS_STRING}")
            exit(1)
        return model_short_name, MODEL_INFO.get(model_short_name)["model_api_name"], MODEL_INFO.get(model_short_name)["model_family"]

    def _send_message_to_openai(self, api_messages: List[Dict[str, str]]) -> Tuple[str, float, str]:
        """Send a message to the OpenAI API and return the response.

           Args:
           - List[Dict[str, str]]: api_messages is a list of messages to send to the model.
             These messages contain only what the api will accept.

           Returns:
           - Tuple[str, float]: The response from the model and the cost of the request and model name (openai).
             Returns an error string if there was a problem.
        """

        spinner = Spinner()

        def send_request():
            nonlocal spinner
            if self.family == "openrouter.ai":
                # Initialize the Openrouter client
                if self._openrouterClient is None:
                    key = os.environ["OPENROUTER_API_KEY"]
                    self._openrouterClient = OpenAI(
                      base_url="https://openrouter.ai/api/v1",
                      api_key=key
                    )
                try:
                    spinner.set_response(self._openrouterClient.chat.completions.create(
                        extra_headers={
                            "HTTP-Referer": "termi-chat",
                            "X-Title": "termi-chat"
                        },
                        model=self.model_api_name,
                        messages=api_messages
                    ))
                except Exception as e:
                    print(f"Error: {e}")
            elif self.family == "openai":
                if self._openaiClient is None:
                    # Initialize the OpenAI client
                    self._openaiClient = OpenAI()
                try:
                    spinner.set_response(self._openaiClient.chat.completions.create(
                        model=self.model_api_name,
                        messages=api_messages
                    ))
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print(f"Unsupported model when trying to send: {self.model_api_name}")

        spinner.start(send_request)

        # Handle the response after spinner finishes
        response = spinner.response

        if response is None:
            warn_message("Timeout condition: Request took too long to complete")

        sys.stdout.flush()

        # OpenAI has no status code -- so if we get a response, we assume 200 OK.
        # See https://community.openai.com/t/http-status-for-chat-completion/541491
        if response:
            print()
            print(f"response = {response}")
            cost_per_input_1k_tokens, cost_per_output_1k_tokens = self._get_model_cost_values(self.model_api_name)
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = input_tokens + output_tokens
            cost_for_input = cost_per_input_1k_tokens * input_tokens / 1000
            cost_for_output = cost_per_output_1k_tokens * output_tokens / 1000
            total_for_both = cost_for_input + cost_for_output

            self._total_cost += total_for_both
            if total_for_both > 0.0:
                warn_message(f"\nCost: ${cost_for_input:.4f} for input, ${cost_for_output:.4f} for output, total: ${total_for_both:.4f}")
            return response.choices[0].message.content, total_for_both, "openai"
        else:
            warn_message(f"\nRequest failed with unknown status code")
            return f"{ANSI_BOLD}{ANSI_RED}Error talking to model {self.model_api_name}: response = {str(response)}{ANSI_RESET}", 0.0, "Error"

    def _send_message_to_local_TGW(self, api_messages: List[Dict[str, str]]) -> Tuple[str, float, str]:
        """Send a message to the text-generation-webui in the background and return immediately.

            Args:
            - List[Dict[str, str]]: api_messages is a list of messages to send to the model.
              These messages contain only what the api will accept.
            - Returns:
           - Tuple[str, float]: The response from the model and the cost of the request, and model name from response.
             Returns an error string if there was a problem.
        """

        # Today, we hardcode this until we can figure out how to load a specific
        # type of model and character.
        #url = "http://192.168.1.52:5089/v1/chat/completions"

        # For runpod.io, use something like this:
        # Create a tunnel (where the pod IP = 207.189.112.60 and ssh port is 43919) like this:
        #   ssh root@207.189.112.60 -L 5005:127.0.0.1:5000 -p 43919 -i ~/.ssh/id_rsa
        url = "http://127.0.0.1:5005/v1/chat/completions"
        headers = {"Content-Type": "application/json"}

        data = {
            "messages": api_messages,
            "mode": "chat",
            "character": self.model_api_name,
        }
        spinner = Spinner()

        def post_request():
            nonlocal spinner
            try:
                # Today, we do a raw request vs. calling a proper api.
                spinner.set_response(requests.post(url, json=data, headers=headers))
            except Exception as e:
                print(f"Error: {e}")

        spinner.start(post_request)

        # Handle the response after spinner finishes
        response = spinner.response

        if response is None:
            warn_message("\nTimeout condition: Request took too long to complete")

        if response and response.status_code == 200:
            sys.stdout.flush()
            result = response.json()

            # Print the model so we know which one we're using
            response_model = result['model']
            marker_message(f"\nmodel = {response_model}")
            cost_per_input_1k_tokens, cost_per_output_1k_tokens = self._get_model_cost_values(self.model_api_name)

            # Get the token counts.
            input_tokens = result['usage']['prompt_tokens']
            output_tokens = result['usage']['completion_tokens']

            total_tokens = input_tokens + output_tokens
            cost_for_input = cost_per_input_1k_tokens * input_tokens / 1000
            cost_for_output = cost_per_output_1k_tokens * output_tokens / 1000
            total_for_both = cost_for_input + cost_for_output

            self._total_cost += total_for_both
            if total_for_both > 0.0:
                warn_message(f"\nCost: ${cost_for_input:.4f} for input, ${cost_for_output:.4f} for output, total: ${total_for_both:.4f}")
            return result["choices"][0]["message"]["content"], total_for_both, response_model
        else:
            sys.stdout.flush()
            if response:
                warn_message(f"Request failed with status code {response.status_code}: {response.text}")
            return f"{ANSI_BOLD}{ANSI_RED}Error talking to model {self.model_api_name}: response = {str(response)}{ANSI_RESET}", 0.0, "Error"

    def get_estimated_tokens(self, message_list: List[Dict[str, str]]) -> int:
        """ Get the estimated number of tokens for a list of messages."""
        tokens = sum(self._get_estimated_tokens_for_message(messages['content']) for messages in message_list)
        return tokens

    def _get_estimated_tokens_for_message(self, message_string: str) -> int:
        """Get the estimated number of tokens for a single message string."""
        return len(TOKEN_ENCODING.encode(message_string))

    def help(self) -> None:
        """Print help message for the methods used when running interactively."""
        print("clear()              start the conversation over (clearing all but system content)")
        print("set_max_context()    set the max context to use")
        print("set_model(tmp_model) set the model to use")
        print("display()            display instance info")
        print("send(str, ask=False) send a message to the assistant; user_input can be empty")
        print("save(filename)       save the conversation context to a file")
        print("view()               print the formatted conversation stored as self.messages")
        print("run_conversation()   start an infinite loop to keep the conversation going")

    def display(self) -> None:
        """Display instance info"""
        print(f"TermiChat instance ({self.name}):")
        print(f"  model            : {self.model}")
        print(f"  model_api_name   : {self.model_api_name}")
        print(f"  family           : {self.family}")
        print(f"  max_context      : {self.max_context}")
        print(f"  assistant_name   : {self.assistant_name}")
        print(f"  user_name        : {self.user_name}")
        print(f"  filename         : {self.filename}")
        print(f"  messages         : {len(self.messages)}")
        print(f"  original_messages: {len(self.original_messages)}")
        print(f"  _total_cost      : {self._total_cost}")
        print(f"  timestamps       : {self.timestamps}")

    def view(self) -> None:
        """Print the formatted conversation stored as self.messages.
           We will always have message[0] which contains the system prompt."""
        if len(self.messages) < 1:
            print("No conversation context to display.")
            return
        print(f"Length of messages: {len(self.messages)}, max_context: {self.max_context}")
        self._print_message(0, self.messages[0])

        # max_context of 0 means we just pass in the system prompt.
        if self.max_context == 0:
            return

        # If we tweaked the max context, we'll show the last max_context
        # of messages
        if self.max_context < len(self.messages):
            rest_of_messages = self.messages[-self.max_context:]
        else:
            rest_of_messages = self.messages[1:]
        for index, message in enumerate(rest_of_messages):
            self._print_message(index + 1, message)

    def clear(self) -> None:
        """Just keep the system message and clear the rest."""
        self.messages = [{"role": "system", "content": self.messages[0]["content"], "timestamp": self._get_timestamp()}]
        self.timestamps = [self._get_timestamp()]
        print("Conversation context cleared. Starting over.")

    def save(self, tmpOutputFilename: str) -> None:
        self._save_to_file(self.filename, self.messages, tmpOutputFilename)
        self.original_messages = json.dumps(self.messages)  # Update original state after saving
        print(f"Context saved to {tmpOutputFilename}.")

        # The new filename becomes the current filename for future saves.
        self.filename = tmpOutputFilename

    def set_max_context(self) -> None:
        """Set the max context to use."""
        if len(self.messages) < 2:
            print("No conversation context so max context cannot be changed.")
            return
        tmp_input = input(f"Enter the max context to use (blank = no change, max = {len(self.messages)-1}): ")
        if len(tmp_input) > 0:
            try:
                tmp_max = int(tmp_input)
                if tmp_max >= len(self.messages):
                    print(f"Invalid max context. Please enter a value less than {len(self.messages)}")
                    return
            except ValueError:
                print("Invalid max context. Please enter a valid integer.")
                return
            self.max_context = tmp_max
            print(f"Max context changed to {self.max_context}.")
        else:
            print(f"Max context not changed.")

    def set_model(self, tmp_model: str) -> None:
        """Set the model to use."""
        self.model, self.model_api_name, self.family = self._get_model_api_and_family(tmp_model)
        self._inform_model_cost(self.model_api_name)
        self.assistant_name, self.user_name = get_names_from_cli(self.model)

    def send(self, user_input: str, confirm: bool = False) -> None:
        if len(user_input) > 0:
            self.messages.append({"role": "user", "content": user_input, "timestamp": self._get_timestamp()})

        api_messages = self._prepare_messages_for_api()

        if confirm:
            # Calculate tokens
            estimated_tokens = self.get_estimated_tokens(api_messages)
            print(f"Estimated tokens to be sent: {estimated_tokens}")

            # Give the user a chance to read their message and send or cancel.
            options = [ f"Send to '{self.model}' assistant", "Cancel" ]
            terminal_menu = TerminalMenu(options)
            selected_option = terminal_menu.show()
            if selected_option is None:
                # Escape was pressed so do nothing.
                confirm = 'cancel'
                self.messages.pop()
                return
            else:
                confirm = options[selected_option]
            if confirm.lower() == 'cancel':
                warn_message("Message canceled.")
                self.messages.pop()
                return

        start_time = time.time()  # Start timing

        if self.family == "openai" or self.family == "openrouter.ai":
            assistant_response, tmp_cost, tmp_response_model = self._send_message_to_openai(api_messages)
        elif self.family == "text-generation-webui":
            assistant_response, tmp_cost, tmp_response_model = self._send_message_to_local_TGW(api_messages)
        else:
            print(f"Unsupported model family: {family}")
            return

        end_time = time.time()  # End timing

        print()
        dashes()
        response_time = end_time - start_time
        warn_message(f"Response time: {response_time:.2f} seconds")

        info_message(f"{self.assistant_name}")
        print(wrap_text(assistant_response))
        self.messages.append({"role": "assistant",
                 "content": assistant_response,
                 "timestamp": self._get_timestamp(),
                 "model": self.model,
                 "family": self.family,
                 "response_seconds": round(response_time, 2),
                 "response_model": tmp_response_model,
                 "cost_dollars": tmp_cost})

    def run_conversation(self):
        # Start an infinite loop to keep the conversation going
        while True:
            user_input = self._get_multiline_input("\nEnter your command (type control-d for options), or your conversation text:")

            if user_input.lower() == 'm' or user_input.lower() == 'menu' or user_input.lower() == '':
                options = list(MENU_ITEMS.keys())
                terminal_menu = TerminalMenu(options)
                selected_option = terminal_menu.show()
                if selected_option is None:
                    # Escape was pressed so do nothing.
                    continue
                user_input = MENU_ITEMS[options[selected_option]]

            if user_input.lower() == 'model':
                options = list(MODEL_MENU_ITEMS.keys())
                terminal_menu = TerminalMenu(options)
                selected_option = terminal_menu.show()
                if selected_option is None:
                    # Escape was pressed so do nothing.
                    print("Model not changed.")
                    continue
                tmp_model = MODEL_MENU_ITEMS[options[selected_option]]
                self.set_model(tmp_model)

            elif user_input.lower() == 'info':
                tmp_info = get_model_info(self.model_api_name)
                print()
                print(tmp_info)
                print()

            elif user_input.lower() == 'names':
                tmp_input = input(f"Enter the assistant name (blank = no change, default = {assistant_name}): ")
                if len(tmp_input) > 0:
                    self.assistant_name = tmp_input
                    print(f"Assistant name changed to {self.assistant_name}.")
                else:
                    print(f"Assistant name not changed.")
                tmp_input = input(f"Enter the user name (blank = no change, default = {user_name}): ")
                if len(tmp_input) > 0:
                    self.user_name = tmp_input
                    print(f"User name changed to {user_name}.")
                else:
                    print(f"User name not changed.")
                continue

            elif user_input.lower() == 'max':
                self.set_max_context()

            elif user_input.lower() == 'view':
                self.view()

            elif user_input.lower() == 'clear':
                self.clear()

            elif user_input.lower() == 'save':
                tmpOutputFilename = input("Enter filename to save the context (enter means current one): ")
                if tmpOutputFilename == "":
                    tmpOutputFilename = self.filename
                self.save(tmpOutputFilename)

            elif user_input.lower() == 'load':
                if self.original_messages != json.dumps(self.messages):
                    warn_message("You have unsaved changes; load anyway?")

                    # Print a menu for yes/no.
                    options = ["Yes", "No"]
                    terminal_menu = TerminalMenu(options)
                    selected_option = terminal_menu.show()
                    if selected_option is None:
                        # Escape was pressed so do nothing.
                        continue
                    if options[selected_option].lower() == "no":
                        continue
                # The new chosen filename becomes the current filename for future saves.
                self.filename, self.messages, self.original_messages = self.check_load_file(self.filename)

            elif user_input.lower() == 'quit':
                if self.original_messages != json.dumps(self.messages):
                    print("You have unsaved changes. Please save your context before quitting.")
                    continue
                print("Quitting.\n")
                break

            elif user_input.lower() == 'exit':

                # If the user has unsaved changes, we'll print a warning.
                if self.original_messages != json.dumps(self.messages):
                    warn_message("You have unsaved changes. Are you sure you want to exit without saving?")
                else:
                    print("Goodbye.\n")
                    break
                # Print a menu for yes/no.
                options = ["Yes", "No"]
                terminal_menu = TerminalMenu(options)
                selected_option = terminal_menu.show()
                if selected_option is None:
                    # Escape was pressed so do nothing.
                    continue
                if options[selected_option].lower() == "yes":
                    warn_message("Exited with unsaved changes.\n")
                    break
            else:

                if user_input.lower() == 'resend':
                    # If the user sends a message, we'll send it to the assistant and then print the response.
                    # We'll also track the time it takes to get the response.
                    if len(self.messages) < 2:
                        print("No conversation context to send to the assistant.")
                        continue
                    print(f"Sending {ANSI_LIGHTBLUE}unchanged{ANSI_RESET} conversation context to {self.model} assistant...")
                    self.send("", True)
                else:
                    # Add the user's input to the messages
                    print(f"Sending conversation context to {self.model} assistant...")
                    self.send(user_input, True)

 
