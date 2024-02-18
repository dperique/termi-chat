#!/usr/bin/env python
import json
import sys
from tabulate import tabulate

# Generate data with: curl -sk https://openrouter.ai/api/v1/models > models.json
# Then use ./tab.py model.json
def process_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Sorting data by context_length in descending order
    sorted_data = sorted(data['data'], key=lambda x: x['context_length'], reverse=True)

    # Preparing data for tabulation
    table_data = []
    for item in sorted_data:
        id = item['id']
        context_length = item['context_length']
        prompt_cost = f"${float(item['pricing']['prompt']) * 1000:.5f}"
        completion_cost = f"${float(item['pricing']['completion']) * 1000:.5f}"
        modality = item['architecture']['modality']
        instruct_type = item['architecture']['instruct_type']
        table_data.append([id, context_length, prompt_cost, completion_cost, modality, instruct_type])

    # Printing the tabulated data
    print(tabulate(table_data, headers=["ID", "Context Length", "Prompt Cost", "Completion Cost", "Modality", "Instruct Type"], tablefmt="grid"))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <path_to_json_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    process_json(file_path)

