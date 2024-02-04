# Termi-Chat: Terminal based LLM chatbot

<div align="center">
    <img src="logo/termi-chat.png" alt="termi-chat logo">
</div>

Termi-Chat is a chatbot similar to the ChatGPT webUI but requires only a terminal.

Some of us like webapges but sometimes you just want a terminal, for the former,
see chat.opanai.com, for the latter, termi-chat is for you.

## Requirements

* Openai API Key
* Python and the openai package (via `pip install openai`)
* Terminal where you can run termi-chat.py

## Features

* Lightweight: all you need is a terminal.
* Colored text for easy reading.
* No streaming -- just give me the answers!
* Save and load your conversation so you can have a longer term conversation
  * Conversations are simple json so you can add to or remove from more easily
  * Conversations are text which means you can archive and search them
    as easily as you can with your notes.  ChatGPT conversations become a part
    of your notes vs. asking over and over for the same thing.
  * Gives a good way to organize and manage your conversations.
* Switch GPT models while retaining the conversation.  If you want deeper
  answers or simpler/faster/cheaper answers, just restart termi-chat using a
  different model.
* Press `<ENTER>` to submit the text after seeing how many tokens (in case you are cost conscious).
* Tracks response times in case you like to know how long it takes to respond.


## Limitations

* No image support


## Environment setup

I use `conda` but you can use any python environment tool.

```bash
conda create -n termi-chat python=3.11
conda activate termi-chat
pip install openai
conda env list
```

## User Interface

* The input method allows you to copy/paste and/or type input including new lines.
  This allows you to format your input for readability.  Use control-d on a line by itself
  to submit the input.
* Time and conversation changes are noted so that you are reminded to save your work
  (though saving is optional).

## Convert ChatGPT UI conversations to saved context

Use [chatgpt-exporter](https://github.com/pionxzh/chatgpt-exporter/tree/master) to export
your conversations from the ChatGPT webui.  `chatgpt-exporter` does a good job
of exporting conversations but the json has a lot of information I don't care to save.
These utilitiy scripts will extract the parts I do care about; one is in bash and another in python:

* [chatgptui_to_simply.py](./utilities/chatgptui_to_simple.py)
* [chatgptui_to_simply.sh](./utilities/chatgptui_to_simple.sh)

NOTE: if you need to debug, the python script will be preferred.

The `chatgpt-exporter` will put a ChatGPT saved conversation (on the left side of the ChatGPT UI)
in a json file named after the ChatGPT conversation title.  The converted file can be loaded
into the [termi-chat](./python/termi-chat.py) using the `load` command.

To use `chatgpt-exporter`, browse to ChatGPT UI, select your conversation, click Export/Json,
then run the utility script above on that file.  The resulting file will be generated based on
the `.title` in the exported json file.

You can do this for any conversation and repeatedly for the same conversation as that conversation
is updated.  This way, you don't have to worry about capturing only the new parts of the
conversation.

NOTE: keep these under source control so you can see that your changes are adding and not
replacing text (if you care about that).  For example, you can do this:

```bash
git init .
git add .
git commit -m 'initial'
```

Then you can keep adding more files.  This is a private git repo you can store somewhere locally
especially if you don't want to share the conversations or don't want them on github.com.  You
will still get history and all github has to offer -- just locally.

## Usage examples

* [Basic usage with just a custom system prompt](./doc/basic_usage.md).

## Build, push, run as container

Bump the version number in `VERSION`.

```bash
make use-podman ;# or make use-docker
make build
podman login -u <YourUserId>
make push
```

For running from a container, you only need `docker` or `podman`.  I create a directory
where my conversations will be saved at `/home/dperique/termi-chats`, set my API key,
and then run:

```bash
mkdir /home/dperique/termi-chats
export OPENAI_API_KEY=sk...
podman run -it --rm \
    -v /home/dperique/termi-chats:/termi-chats \
    -e OPENAI_API_KEY=${OPENAI_API_KEY} \
    dperique/termi-chat:${VERSION} --load /termi-chats/dennis_golang.json --model gpt3.5 --names Cassy,Dennis
```

## Todo

* the context that keeps building will make our usage cost keep getting bigger
  * make some kind of pipeline that can prune out certain context we don't care to remember
    * like code -- no one needs to remember multiple versions of programs so prune these out.
    * any ai generated text -- or just save some bullet points so it remembers roughly what it told me
    * any extra stuff that doesn't matter like small talk
    * think of things you would remember in human conversations and what most people tend to forget
  * add a mechanism so that if the user asks about something, maybe looking for "remember when...",
    we can search for context and swap that in so that the context is smaller everytime we call the api -- maybe memgpt.
