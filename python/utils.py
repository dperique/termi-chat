import textwrap

# Constants for ANSI color codes
ANSI_LIGHTBLUE = "\033[94m"
ANSI_RED = "\033[91m"
ANSI_GREEN = "\033[92m"
ANSI_YELLOW = "\033[93m"
ANSI_BOLD = "\033[1m"
ANSI_RESET = "\033[0m"

_cached_model_info = None

def warn_message(message_str: str) -> None:
    """Print a warning message in red."""
    print(f"{ANSI_RED}{ANSI_BOLD}{message_str}{ANSI_RESET}")

def marker_message(message_str: str) -> None:
    """Print a message in light blue."""
    print(f"{ANSI_LIGHTBLUE}{ANSI_BOLD}{message_str}{ANSI_RESET}")

def info_message(message_str: str) -> None:
    """Print an informational message in green."""
    print(f"{ANSI_GREEN}{ANSI_BOLD}{message_str}{ANSI_RESET}")

def dashes() -> None:
    """Print 80 dashes for separation."""
    marker_message("-" * 80)

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

def get_model_info(model_api_name: str) -> str:
    """ Call openrouter.ai to get model information as a json and then return it for this model_api_name.
        Cache the result since it's not super quick"""
    import requests
    url = f"https://openrouter.ai/api/v1/models"
    global _cached_model_info
    if _cached_model_info is None:
        try:
            response = requests.get(url)
            _cached_model_info = response.json()['data']
        except Exception as e:
            print(f"Error getting model info for {model_api_name}: {e}")
            ret_val = str(e)
    for model_info in _cached_model_info:
        if model_info['id'] == model_api_name:
            # a return value looks like this:
            # {'id': 'open-orca/mistral-7b-openorca', 'name': 'Mistral OpenOrca 7B', 'description': 'A fine-tune of Mistral using the OpenOrca dataset. First 7B model to beat all other models <30B.', 'pricing': {'prompt': '0.0000001425', 'completion': '0.0000001425'}, 'context_length': 8192, 'architecture': {'modality': 'text', 'tokenizer': 'Mistral', 'instruct_type': 'gpt'}, 'top_provider': {'max_completion_tokens': None, 'is_moderated': False}, 'per_request_limits': None}
            # print that out nicely formatted line by line
            return f"Model info for {model_api_name}:\n" + "\n".join([f"{k}: {v}" for k, v in model_info.items()])
    else:
        return f"Model info for {model_api_name} not found"
