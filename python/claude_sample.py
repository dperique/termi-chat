import os
import anthropic

client = anthropic.Anthropic(
    api_key = os.environ.get("ANTHROPIC_API_KEY")
)

message = client.messages.create(
    model="claude-2.1",
    max_tokens=1000,
    temperature=0,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "what is the distance the moon"
                }
            ]
        }
    ]
)
print(message.content)
print(message.content[0].text)
print(message.usage.input_tokens)
print(message.usage.output_tokens)
t = dict(message)
print(t.get('usage').input_tokens)
print(t.get('usage').output_tokens)
print(t.keys())