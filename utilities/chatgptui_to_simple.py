#!/usr/bin/env python3
import json
import sys
from datetime import datetime

# This converts from chatgpt webui conversation to a simple json format
# suitable for ingestion by termi-chat.

if len(sys.argv) != 2:
    print("Usage: python chatgptui_to_simple.py <chatgptui_output_file>")
    sys.exit(1)

input_file = sys.argv[1]

def format_timestamp(timestamp):
    if timestamp != "Time_not_available":
        return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d-%H:%M')
    return "Time_not_available"

try:
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

        output_data = []
        for entry_id, entry in data['mapping'].items():
            message = entry.get('message')
            if message:
                role = message['author']['role'] if message.get('author') else "unknown"
                content_parts = message['content']['parts'] if message.get('content') and 'parts' in message['content'] else []

                # Ensure content_parts are strings
                content_parts = [str(part) for part in content_parts]

                content = ' '.join(content_parts)
                timestamp = format_timestamp(message['create_time']) if message.get('create_time') else "Time_not_available"
                output_data.append({
                    'role': role,
                    'content': content,
                    'timestamp': timestamp
                })

        output_filename = data['title'].replace(" ", "_").replace(":", "_") + ".json"
        with open(output_filename, 'w', encoding='utf-8') as output_file:
            json.dump(output_data, output_file, ensure_ascii=False, indent=2)

        print(f"Conversion complete. Output saved to {output_filename}")

except FileNotFoundError:
    print(f"File not found: {input_file}")
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Invalid JSON format in file: {input_file}")
    sys.exit(1)