import os
import sys
import openai
import streamlit as st
from streamlit_chat import message
from streamlit_shortcuts import add_keyboard_shortcuts

# Sometimes we might want a UI.  Streamlit is pretty lightweight and easy to use
# so we'll make one.
# Run like this from the command line for 3 different conversations:
# streamlit run --server.port 8501 --theme.base dark app.py conversation1
# streamlit run --server.port 8502 --theme.base dark app.py conversation2
# streamlit run --server.port 8503 --theme.base dark app.py conversation3
chat_title = "TermiChat"
if len(sys.argv) > 1:
    chat_title = sys.argv[1]

# Setting page title and header and allow wide mode (so you can widen your browser
# to see the chat history better).
st.set_page_config(page_title=chat_title, layout="wide", page_icon=":robot_face:")
st.markdown("<h2 style='text-align: center;'>Termi-chat 🔥</h2>", unsafe_allow_html=True)

# Get this from .streamlit/secrets.toml
#   OPENAI_API_KEY = "..."
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Initialise session state variables

if 'generated' not in st.session_state:
    # Tracks the bot responses
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    # Tracks the user inputs
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    # Tracks the what we send to the model (including past messages and the current user input)
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
if 'model_name' not in st.session_state:
    # Keep model name equal to the actual model name for simplicity when adding a new one
    st.session_state['model_name'] = []

# These 3 track cost for paid models to help the user now what they're spending
if 'cost' not in st.session_state:
    st.session_state['cost'] = []
if 'total_tokens' not in st.session_state:
    st.session_state['total_tokens'] = []
if 'total_cost' not in st.session_state:
    st.session_state['total_cost'] = 0.0

# All of these are from a locally running ollama plus gpt3.5 and gpt4
# The "test" model is for error testing
models = ["llama3:8b", "deepseek-coder:6.7b", "llama2-uncensored:7b", "dolphin-mixtral:8x7b-v2.7-q4_K_M", "test", "gpt-3.5-turbo", "gpt-4"]

# Sidebar - used to show the conversation title and model selection
st.sidebar.title(chat_title)
model_name = st.sidebar.radio("Choose a model:", (models))
counter_placeholder = st.sidebar.empty()
counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")
clear_button = st.sidebar.button("Clear Conversation", key="clear")
reload_button = st.sidebar.button("Reload App", key="reload")

# Map model names to OpenAI model IDs
model = model_name

# Reload the app in case of changes (might not need this if we keep the top menu items active)
if reload_button:
    st.rerun()

# Reset all variables including conversation history
if clear_button:
    st.session_state['generated'] = []
    st.session_state['past'] = []
    st.session_state['messages'] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    st.session_state['number_tokens'] = []
    st.session_state['model_name'] = []
    st.session_state['cost'] = []
    st.session_state['total_cost'] = 0.0
    st.session_state['total_tokens'] = []
    counter_placeholder.write(f"Total cost of this conversation: ${st.session_state['total_cost']:.5f}")

# Get responses from ollama models.  Cost = $0
def ollama_generate_response(prompt):

    from ollama import Client
    client = Client(host='http://localhost:11434')

    st.session_state['messages'].append({"role": "user", "content": prompt})
    try:
        completion = client.chat(
            model=model,
            messages=st.session_state['messages']
        )
        response = completion['message']['content'].strip()
    except Exception as e:
        error_text = f"Error in ollama server: Error: {str(e)}"
        response = error_text
        print(response)

    st.session_state['messages'].append({"role": "assistant", "content": response})

    total_tokens = 0
    prompt_tokens = 0
    completion_tokens = 0
    return response, total_tokens, prompt_tokens, completion_tokens

# Get responses from chatgpt; cost is based on tokens and model type
def generate_response(prompt):

    from openai import OpenAI
    client = OpenAI()

    st.session_state['messages'].append({"role": "user", "content": prompt})
    try:
        completion = client.chat.completions.create(
            model=model,
            messages=st.session_state['messages']
        )
        response = completion.choices[0].message.content.strip('\n')
    except Exception as e:
        error_text = f"Error in openai server: Error: {str(e)}"
        response = error_text
        print(response)
        return response, 0,0,0

    st.session_state['messages'].append({"role": "assistant", "content": response})

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
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')
        add_keyboard_shortcuts({'Shift+Enter': submit_button})

    if submit_button and user_input:
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)

        if "gpt" in model.lower():
            output, total_tokens, prompt_tokens, completion_tokens = generate_response(user_input)
        else:
            output, total_tokens, prompt_tokens, completion_tokens = ollama_generate_response(user_input)
        my_bar.progress(100, text=progress_text)
        my_bar.empty()
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)
        st.session_state['model_name'].append(model_name)
        st.session_state['total_tokens'].append(total_tokens)

        # see https://openai.com/pricing#language-models
        # for other models (like ollama based), we don't update cost.
        if model_name == "gpt-3.5-turbo":
            cost = total_tokens * 0.002 / 1000
        elif model_name == "gpt-4":
            cost = (prompt_tokens * 0.03 + completion_tokens * 0.06) / 1000
        else:
            cost = 0.0

        st.session_state['cost'].append(cost)
        st.session_state['total_cost'] += cost

if st.session_state['generated']:
    with response_container:

        # Draw the interleaved conversation.
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i), avatar_style="adventurer-neutral")
            if "gpt" in model.lower():
                st.write(
                    f"Model: {st.session_state['model_name'][i]}; Tokens: {st.session_state['total_tokens'][i]}; Cost: ${st.session_state['cost'][i]:.5f}")
                counter_placeholder.write(f"Total cost of conversation: ${st.session_state['total_cost']:.5f}")
