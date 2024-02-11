#!/usr/bin/env python

import os
import sys
from TermiChat import TermiChat, get_file_or_dir_from_cli, get_model_from_cli, get_names_from_cli, get_max_context_from_cli, help_message

# If user did --load filename, we'll load the file. Otherwise, we'll ask them to choose a system prompt.
file_or_dir_from_cli = get_file_or_dir_from_cli()

# If user did --model modelname, we'll use that model. Otherwise, we'll use DEFAULT_MODEL.
model = get_model_from_cli()

# if user did --names name1,name2, we'll use those names. Otherwise, we'll use the default names.
assistant_name, user_name = get_names_from_cli(model)

# if user did --max, we'll use that max context. Otherwise, we'll use the default max context.
max_context = get_max_context_from_cli()

if "--help" in sys.argv or "-h" in sys.argv:
    help_message()
    exit(0)

instance = TermiChat("Conversation1", model, max_context, assistant_name, user_name, file_or_dir_from_cli)
instance.run_conversation()