#!/bin/bash

# Run this like this:
#
# ./utilities/select.sh /path/to/termi-chats
#
if [ $# -eq 0 ]; then
    echo "Usage: $0 <termi-chats storage directory>"
    exit 1
fi

termi_chats_dir="$1"

# Define your conversations using indexed arrays
conversations=(
		"dennis_golang.json,Cassy,Dennis,gpt3.5"
	   	"Talk_to_Jocko.json,Jocko,Dennis,gpt3.5"
		"basic_dennis.json-local,Cassy,Dennis,Cassie"
		"basic_dennis.json,Dennis,Mr-gpt3.5,gpt3.5"
)

show_menu() {
    echo
    echo "Using termi-chat version $(cat VERSION)"
    echo
    echo "Select a conversation:"
    for i in "${!conversations[@]}"; do
        IFS=',' read -r -a chat <<< "${conversations[$i]}"
        echo "$((i+1))) ${chat[0]}"
    done
    echo "Enter your choice (number):"
}

show_menu
read -r choice_index
let "choice = choice_index - 1"

if [[ -z "${conversations[$choice]}" ]]; then
    echo "Invalid choice"
    exit 1
fi

IFS=',' read -r -a chat_details <<< "${conversations[$choice]}"
conversation=${chat_details[0]}
names=${chat_details[1]},${chat_details[2]}
model=${chat_details[3]}

docker run -it --rm \
    -v "${termi_chats_dir}:/termi-chats" \
    -e OPENAI_API_KEY=${OPENAI_API_KEY} \
	--net=host \
    dperique/termi-chat:$(cat VERSION) --load /termi-chats/${conversation} --model ${model} --names ${names}

