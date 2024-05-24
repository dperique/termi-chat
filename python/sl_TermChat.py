import os
import json
import sys
from datetime import datetime
import openai
import streamlit as st
from streamlit_chat import message
from streamlit_shortcuts import add_keyboard_shortcuts

# Sometimes we might want a UI.  Streamlit is pretty lightweight and easy to use
# so we'll make one.
# Run like this from the command line for 3 different conversations:
# streamlit run --browser.gatherUsageStats false --server.port 8501 --theme.base dark python/sl_TermChat.py conversation1
# streamlit run --browser.gatherUsageStats false --server.port 8502 --theme.base dark python/sl_TermChat.py conversation2
# streamlit run --browser.gatherUsageStats false --server.port 8503 --theme.base dark python/sl_TermChat.py conversation3
chat_title = "TermiChat"
if len(sys.argv) > 1:
    chat_title = sys.argv[1]

# Setting page title and header and allow wide mode (so you can widen your browser
# to see the chat history better).
st.set_page_config(page_title=chat_title, layout="wide", page_icon=":robot_face:")
st.header(f"Termi-chat 🔥: {chat_title}")

# Get this from .streamlit/secrets.toml
#   OPENAI_API_KEY = "..."
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Initialise session state variables
DEFAULT_SYSTEM_CONTEXT = "You are a helpful assistant."
if 'output_mode' not in st.session_state:
    # Tracks the output mode (e.g., chat, code, etc.)
    st.session_state['output_mode'] = "old"
if 'assistant' not in st.session_state:
    # Tracks the bot responses
    st.session_state['assistant'] = []
if 'user' not in st.session_state:
    # Tracks the user inputs
    st.session_state['user'] = []
if 'system_context' not in st.session_state:
    # Tracks the system context
    st.session_state['system_context'] = DEFAULT_SYSTEM_CONTEXT
if 'messages' not in st.session_state:
    # Tracks what we send to the model (including past messages and the current user input)
    st.session_state['messages'] = [
        {"role": "system", "content": st.session_state['system_context']}
    ]
if 'model_name' not in st.session_state:
    # Keep model name equal to the actual model name for simplicity when adding a new one
    st.session_state['model_name'] = []

if 'uploaded_file' not in st.session_state:
    st.session_state['uploaded_file'] = None

# Hacky but works: we need to track the key for the file uploader so we can clear it
# when a new file is uploaded.
if 'uploaded_file_key' not in st.session_state:
    st.session_state['uploaded_file_key'] = 1

if 'file_name' not in st.session_state:
    st.session_state['file_name'] = "termi-chat1.json"

if 'timestmp' not in st.session_state:
    st.session_state['timestamp'] = []

# These 3 track cost for paid models to help the user now what they're spending
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0

# Use a reasonable start value for max_tokens; the user can change it
# using the slider.
max_tokens = 512

# We use a map for the model name and the API type.  This is so we can
# use the correct API for the model.  We have 4 types of models:
# 1. ollama - a locally running model
# 2. openai - a model from OpenAI
# 3. openrouter - a model from OpenRouter
# 4. deepseek - a model from DeepSeek
# The "test" model is for error testing
# For paid models, we track the cost of the conversation so add code below
# to calculate cost and a comment to the link to the pricing page.
# see https://openai.com/pricing#language-models
# see https://openrouter.ai/models (cost is differet for each model)
# for other models (like ollama based), we don't update cost.
model_map = {
    "llama3:8b": {"vendor": "ollama", "context_size": 4096, "input_token_cost": 0.1, "output_token_cost": 0.1},
    "deepseek-coder:6.7b": {"vendor": "ollama", "context_size": 4096, "input_token_cost": 0, "output_token_cost": 0},
    "llama2-uncensored:7b": {"vendor": "ollama", "context_size": 4096, "input_token_cost": 0, "output_token_cost": 0},
    "wizard-vicuna-uncensored:13b": {"vendor": "ollama", "context_size": 4096, "input_token_cost": 0, "output_token_cost": 0},
    "dolphin-mixtral:8x7b-v2.7-q4_K_M": {"vendor": "ollama", "context_size": 4096, "input_token_cost": 0, "output_token_cost": 0},
    "codellama:13b-python-q4_K_M": {"vendor": "ollama", "context_size": 4096, "input_token_cost": 0, "output_token_cost": 0},
    "llama3-gradient:8b": {"vendor": "ollama", "context_size": 4096, "input_token_cost": 0, "output_token_cost": 0},
    "--- Below spends Money ---": "ollama",
    "gpt-3.5-turbo-0125": {"vendor": "openai", "context_size": 16384, "input_token_cost": 0.50, "output_token_cost": 1.50},
    "gpt-4o": {"vendor": "openai", "context_size": 128000, "input_token_cost": 5.00, "output_token_cost": 15.00},
    "gpt-4-turbo-2024-04-09": {"vendor": "openai", "context_size": 128000, "input_token_cost": 10.00, "output_token_cost": 30.00},
    "mistralai/mixtral-8x7b-instruct": {"vendor": "openrouter", "context_size": 32768, "input_token_cost": 0.24, "output_token_cost": 0.24},
    "openai/gpt-3.5-turbo-0125": {"vendor": "openrouter", "context_size": 16384, "input_token_cost": 0.50, "output_token_cost": 1.50},
    "anthropic/claude-3-haiku": {"vendor": "openrouter", "context_size": 200000, "input_token_cost": 0.25, "output_token_cost": 1.25},
    "deepseek-chat": {"vendor": "deepseek", "context_size": 32768, "input_token_cost": 0.14, "output_token_cost": 0.28},
    "deepseek-coder": {"vendor": "deepseek", "context_size": 16384, "input_token_cost": 0.14, "output_token_cost": 0.28},
}

def calculate_cost(prompt_tokens, completion_tokens, model_name):
    cost = 0.0
    if model_name in model_map:
        input_token_cost = model_map[model_name].get("input_token_cost", 0)
        output_token_cost = model_map[model_name].get("output_token_cost", 0)
        cost = (prompt_tokens * input_token_cost + completion_tokens * output_token_cost) / 1000000
    else:
        print(f"Model {model_name} not found in our model_map cost list")
        return f"cost is invalid for this model: {model_name}"
    return cost

# Sidebar - used to show the conversation title and model selection
with st.sidebar:
    st.title(chat_title)
    st.form(key='conversation_form', )

    # Create the model selector based on the keys of models_map.
    model_menu_items = list(model_map.keys())
    selected_model_name = st.radio("Choose a model:", model_menu_items)
    if model_map[selected_model_name]['input_token_cost'] > 0 or model_map[selected_model_name]['output_token_cost'] > 0:
        max_tokens = st.slider("Max tokens", min_value=20,
                                             max_value=model_map[selected_model_name]['context_size'],
                                             value=512, step=1)
    temperature = st.slider("temperature", min_value=0.0, max_value=2.0, value=0.8, step=.1)
    counter_placeholder = st.empty()
    tmp_input_cost = model_map[selected_model_name].get("input_token_cost", 0)
    tmp_output_cost = model_map[selected_model_name].get("output_token_cost", 0)
    counter_placeholder.write(f"Total cost (model: \${tmp_input_cost:.2f}, \${tmp_output_cost:.2f}): ${st.session_state['total_cost']:.2f}")
    uploaded_file = st.file_uploader("Load Conversation", type="json", key=f"load{st.session_state['uploaded_file_key']}", help="Load a conversation from a JSON file")

    file_name = st.text_input('File to export to:', 'termi-chat1.json')
    users_name= st.text_input('User name:', 'Dennis')
    system_context = st.text_area('System context:', st.session_state['system_context'], height=100)

    # Create columns for buttons; this gets then side by side
    col1, col2 = st.columns(2, gap='small')
    clear_button = col1.button("Clear", key="clear", help="Clear the conversation history")
    save_button = col1.button("Save", key="save", help="Save the conversation to a JSON file")
    dump_button = col2.button("Dump", key="dump", help="Dump the conversation history to the console")
    refresh_button = col2.button("Update", key="refresh", help="Refresh the page")
    switch_mode = col2.button("Style", key="switch", help="Switch conversation output style")

if system_context != st.session_state['system_context']:
    # The system prompt has changed, so apply it to our saved messages.
    st.session_state['system_context'] = system_context
    new_messages = st.session_state['messages'][1:]
    st.session_state['messages'] = []
    st.session_state['messages'].append({"role": "system", "content": st.session_state['system_context']})
    for msg in new_messages:
        st.session_state['messages'].append(msg)

if switch_mode:
    if st.session_state['output_mode'] == "old":
        st.session_state['output_mode'] = "new"
    else:
        st.session_state['output_mode'] = "old"

if save_button:
    # Serialize and save the conversation to a JSON string
    conversation_json = json.dumps(st.session_state['messages'], indent=4)

    # Create a download button for the JSON string
    st.sidebar.download_button(label="Download Conversation",
                               data=conversation_json,
                               file_name=file_name,
                               mime="application/json")

#print(f"\nUploaded file: {uploaded_file}")
#print(f"\nSession file: {st.session_state['uploaded_file']}")
if uploaded_file != None and uploaded_file != st.session_state['uploaded_file']:
    string_data = uploaded_file.getvalue().decode("utf-8")
    data = json.loads(string_data)
    # Update the session state with the loaded conversation
    if len(data) > 0 and data[0]['role'] == "system":
        system_context = data[0]['content']
        new_messages = data[1:]
    else:
        system_context = DEFAULT_SYSTEM_CONTEXT
        new_messages = data
    st.session_state['system_context'] = system_context
    st.session_state['messages'] = []
    st.session_state['messages'].append({"role": "system", "content": system_context})
    for msg in new_messages:
        st.session_state['messages'].append(msg)
        if msg['role'] == "assistant":
            # Protect against missing fields in the JSON file
            st.session_state['model_name'].append(msg.get('model', "None"))
            st.session_state['total_tokens'].append(msg.get('total_tokens', 0.0))
            st.session_state['cost'].append(msg.get('cost', 0.0))
            st.session_state['timestamp'].append(msg.get('timestamp', "2024-09-09-09:09"))

    st.session_state['system_context'] = system_context
    print(f"Loaded conversation: {uploaded_file}")

    # Fill in the user and assistant lists
    st.session_state['user'] = []
    st.session_state['assistant'] = []
    for msg in new_messages:
        if msg['role'] == "user":
            st.session_state['user'].append(msg['content'])
        elif msg['role'] == "assistant":
            st.session_state['assistant'].append(msg['content'])

    if len(st.session_state['assistant']) != len(st.session_state['user']):
        print("Error loading: assistant and user lists are not the same length")
    st.session_state['uploaded_file'] = uploaded_file

    # Increment the key and refresh so the file uploader will clear
    st.session_state['uploaded_file_key'] += 1
    st.rerun()

#print("running")
if refresh_button:
    print("")
if dump_button:
    json.dump(st.session_state['messages'], sys.stdout, indent=4)
    print("")
    # flush the output buffer
    sys.stdout.flush()

# Reset all variables including conversation history
if clear_button:
    st.session_state['assistant'] = []
    st.session_state['user'] = []
    st.session_state['messages'] = [
        {"role": "system", "content": system_context}
    ]
    st.session_state['number_tokens'] = []
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_cost'] = 0.0
    st.session_state['total_tokens'] = []
    #counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")

# Take a list of messages and strip anything but role and content
# because the api calls only want role and content.
def extract_role_and_content(input_messages):
    messages = []
    for msg in input_messages:
        messages.append({"role": msg["role"], "content": msg["content"]})
    return messages

# Get responses from ollama models.  Cost = $0
# Sadly, ollma api doesn't support max_tokens so we can't use it.
# https://github.com/ollama/ollama/blob/4ec7445a6f678b6efc773bb9fa886d7c9b075577/docs/modelfile.md#valid-parameters-and-values
# default temperature = 0.8
def ollama_generate_response(model, max_tokens, messages, temperature):

    from ollama import Client
    client = Client(host='http://localhost:11434')

    try:
        completion = client.chat(
            model=model,
            messages=messages,
            options = {
                "temperature": temperature
            }
        )
        response = completion['message']['content'].strip()
    except Exception as e:
        error_text = f"Error in ollama server: Error: {str(e)}"
        response = error_text
        return response, 0, 0, 0

    prompt_tokens = completion['eval_count']
    completion_tokens = completion['prompt_eval_count']
    total_tokens = prompt_tokens + completion_tokens

    return response, total_tokens, prompt_tokens, completion_tokens

# Get responses from chatgpt; cost is based on tokens and model type
# See ./.streamlist/secrets.toml for environment variants visible to
# streamlit.
def generate_response(model, max_tokens, messages, temperature):

    from openai import OpenAI
    from os import getenv

    if model_map[model]['vendor'] == "openrouter":

        # Openrouter can use the OpenAI API but we need their base URL and API key
        base_url = "https://openrouter.ai/api/v1"
        api_key=getenv("OPENROUTER_API_KEY")
        client = OpenAI(base_url=base_url, api_key=api_key)

    elif model_map[model]['vendor'] == "deepseek":

        # Deepseek models can use the OpenAI API but we need their base URL and API key
        base_url = "https://api.deepseek.com/"
        api_key=getenv("DEEPSEEK_API_KEY")
        client = OpenAI(base_url=base_url, api_key=api_key)

    elif model_map[model]['vendor'] == "openai":
        api_key = getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)
    else:
        response = f"Error: model {model} not found in our model_map list"
        return response, 0, 0, 0

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature
        )
        response = completion.choices[0].message.content.strip('\n')
    except Exception as e:
        error_text = f"Error in {model_map[model]['vendor']} server: Error: {str(e)}"
        response = error_text
        return response, 0, 0, 0

    total_tokens = completion.usage.total_tokens
    prompt_tokens = completion.usage.prompt_tokens
    completion_tokens = completion.usage.completion_tokens
    return response, total_tokens, prompt_tokens, completion_tokens


# container for chat history
response_container = st.container()
# container for text box
prompt_container = st.container()

with prompt_container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area(f"{users_name}:", key='input', height=200)
        submit_button = st.form_submit_button(label='Send')
        add_keyboard_shortcuts({'Shift+Enter': submit_button})

    if submit_button and user_input:

        # Pass in a copy of the messages in case something goes wrong.  This protects
        # against having a user message without a matching assistant message. We also
        # need a version of the messages list with just role and content for the API.
        tmp_messages = extract_role_and_content(st.session_state['messages'])
        tmp_messages.append({"role": "user", "content": user_input})

        # During inference, the user can click buttons which will abort the inference.
        with st.spinner("Thinking..."):
            if model_map[selected_model_name]['vendor'] == "openai" or \
                model_map[selected_model_name]['vendor'] == "openrouter" or \
                model_map[selected_model_name]['vendor'] == "deepseek":
                output, total_tokens, prompt_tokens, completion_tokens = generate_response(selected_model_name, max_tokens, tmp_messages, temperature)
            elif model_map[selected_model_name]['vendor'] == "ollama":
                output, total_tokens, prompt_tokens, completion_tokens = ollama_generate_response(selected_model_name, max_tokens, tmp_messages, temperature)
            else:
                output = f"Error: model {selected_model_name} not found in our list"
                total_tokens = prompt_tokens = completion_tokens = 0

        st.session_state['user'].append(user_input)
        st.session_state['assistant'].append(output)
        st.session_state['model_name'].append(selected_model_name)
        st.session_state['total_tokens'].append(total_tokens)

        cost = calculate_cost(prompt_tokens, completion_tokens, selected_model_name)

        # Only after we successfully get a response do we update the messages with
        # both user and assistant messages.
        st.session_state['messages'].append({"role": "user", "content": user_input})
        st.session_state['messages'].append({"role": "assistant", "content": output,
                                             "timestamp": datetime.now().strftime("%Y-%m-%d-%H:%M"),
                                             "model": selected_model_name,
                                             "cost": cost })

        st.session_state['cost'].append(cost)
        st.session_state['total_cost'] += cost

if st.session_state['assistant']:
    with response_container:

        # Draw the interleaved conversation.
        for i in range(len(st.session_state['assistant'])):
            #with st.chat_message('user', avatar='🧑‍💻'):
            # with st.chat_message('user'):
            #     st.write(st.session_state['user'][i])
            message(st.session_state['user'][i], is_user=True, key=str(i) + '_user')
            if st.session_state['output_mode'] == "old":
                message(st.session_state['assistant'][i].replace('\t', '    '), key=str(i), avatar_style='adventurer')
            else:
                # 👱‍♀️ , 👱‍♀️, 🧑🏻‍🦰
                with st.chat_message('assistant', avatar='https://raw.githubusercontent.com/dataprofessor/streamlit-chat-avatar/master/bot-icon.png'):
                     st.write(st.session_state['assistant'][i].replace('\t', '    '))
            st.write(f"Model: {st.session_state['model_name'][i]}; Tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}")
            counter_placeholder.write(f"Total cost of conversation: ${st.session_state['total_cost']:.5f}")
