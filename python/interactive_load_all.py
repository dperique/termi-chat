# Load these all up and then you can interact with each individually

from TermiChat import TermiChat, get_file_or_dir_from_cli, get_model_from_cli, get_names_from_cli, get_max_context_from_cli, help_message

cassie = TermiChat   ("Cassie Talk",    "Cassie",    10, "Cassie",       "Dennis", "../termi-chats")
assistant = TermiChat("Assistant Talk", "Assistant", 10, "Assistant AI", "Dennis", "../termi-chats")
gpt3 = TermiChat     ("gpt3.5 Talk",    "gpt3.5",    10, "gpt3.5 AI",    "Dennis", "../termi-chats")
gpt4 = TermiChat     ("gpt4 Talk",      "gpt4",      10, "gpt4 AI",      "Dennis", "../termi-chats")
