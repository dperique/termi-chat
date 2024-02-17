#!/bin/bash

# If VERSION doesn't exist, create it and put 0.5 in it.
if [ ! -f VERSION ]; then
    echo "0.6" > VERSION
fi

# Make a sample file to test with (Assistant is free, use gpt3.5 if you want to pay
# but you'll need an OPENAI_API_KEY).
echo "[
  {
  \"role\": \"system\",
  \"content\": \"You are a helpful assistant; I am an inquisitive and happy software engineer asking question.\"
  }
]" > ./termi-chats/newfile.json

echo "Starting termi-chat with the sample file ..."
echo
./python/termi-chat.py --load termi-chats/newfile.json --model Assistant --names "AI Assistant",Dennis
