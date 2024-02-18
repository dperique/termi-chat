#!/usr/bin/env python

"""
Used to generate the MODEL_INFO dict in case openrouter.ai updates it's list of
supported LLMs.  Use models.json as the input file.
"""
import json
import sys

def process_json_to_dict(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Initialize the resulting dictionary
    result_dict = {}

    # Assuming 'data' is the key that contains the list of models
    for item in data['data']:
        model_id = item['id']
        prompt_cost = float(item['pricing']['prompt']) * 1000
        completion_cost = float(item['pricing']['completion']) * 1000

        result_dict[f"openrouter.ai/{model_id}"] = {
            "model_api_name": model_id,
            "model_family": "openrouter.ai",
            "cost_input": round(prompt_cost, 5),
            "cost_output": round(completion_cost, 5)
        }

    # Print the resulting dictionary
    print(json.dumps(result_dict, indent=4))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_json_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    process_json_to_dict(file_path)

