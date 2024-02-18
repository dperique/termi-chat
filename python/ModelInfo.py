# When you add a new model, add it to the MODEL_INFO dictionary.
# See https://openai.com/pricing#language-models for pricing.
# The first model is the default.
MODEL_INFO = {
    "gpt3.5": {
        # 16K context, optimized for dialog
        "model_api_name": "gpt-3.5-turbo-0125",
        "model_family": "openai",
        "cost_input": 0.0005,
        "cost_output": 0.0015
    },
    "gpt4": {
        "model_api_name": "gpt-4-0613",
        "model_family": "openai",
        "cost_input": 0.01,
        "cost_output": 0.03
    },
    "Cassie": {
        # 4K context using whatever is running on the text-generation-webui
        "model_api_name": "Cassie",
        "model_family": "text-generation-webui",
        "cost_input": 0.01,
        "cost_output": 0.03
    },
    "Assistant": {
        # 4K context using whatever is running on the text-generation-webui
        "model_api_name": "Assistant",
        "model_family": "text-generation-webui",
        "cost_input": 0.0,
        "cost_output": 0.0
    }
}