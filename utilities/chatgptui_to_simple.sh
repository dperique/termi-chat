#!/bin/bash

# This script is used to convert the output of chatgptui to a json file
# It does pretty much the same as the python equivalent, but it's a bit
# simple in that it just relies on jq.  It's simple but has limitations
# and it probably harder to debug.

if [ "$#" -ne 1 ]; then
  echo "Usage: bash chatgptui_to_simple.sh <chatgptui_output_file>"
  exit 1
fi
jq '
  [
    .mapping[] | select(.message != null) | {
       role: .message.author.role,
       content: .message.content.parts | join(" "),
       timestamp: (.message.create_time | if . then todate else "Time_not_available" end)
    }
  ]
 ' $1 > "$(jq -r '.title | gsub(" "; "_") | gsub(":"; "_")' $1).json"
