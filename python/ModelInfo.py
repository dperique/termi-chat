# When you add a new model, add it to the MODEL_INFO dictionary.
# See https://openai.com/pricing#language-models for pricing.
# The first model is the default.
MODEL_INFO = {
    "gpt-3.5-turbo-0125": {
        # 16K context, optimized for dialog
        "model_api_name": "gpt-3.5-turbo-0125",
        "model_family": "openai",
        "cost_input": 0.0005,
        "cost_output": 0.0015
    },
    "gpt-4-0613": {
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
    },
    "openrouter.ai/nousresearch/nous-capybara-34b": {
        "model_api_name": "nousresearch/nous-capybara-34b",
        "model_family": "openrouter.ai",
        "cost_input": 0.0007,
        "cost_output": 0.0028
    },
    "openrouter.ai/nousresearch/nous-capybara-7b:free": {
        "model_api_name": "nousresearch/nous-capybara-7b:free",
        "model_family": "openrouter.ai",
        "cost_input": 0.0,
        "cost_output": 0.0
    },
    "openrouter.ai/mistralai/mistral-7b-instruct:free": {
        "model_api_name": "mistralai/mistral-7b-instruct:free",
        "model_family": "openrouter.ai",
        "cost_input": 0.0,
        "cost_output": 0.0
    },
    "openrouter.ai/gryphe/mythomist-7b:free": {
        "model_api_name": "gryphe/mythomist-7b:free",
        "model_family": "openrouter.ai",
        "cost_input": 0.0,
        "cost_output": 0.0
    },
    "openrouter.ai/undi95/toppy-m-7b:free": {
        "model_api_name": "undi95/toppy-m-7b:free",
        "model_family": "openrouter.ai",
        "cost_input": 0.0,
        "cost_output": 0.0
    },
    "openrouter.ai/openrouter/cinematika-7b:free": {
        "model_api_name": "openrouter/cinematika-7b:free",
        "model_family": "openrouter.ai",
        "cost_input": 0.0,
        "cost_output": 0.0
    },
    "openrouter.ai/jondurbin/bagel-34b": {
        "model_api_name": "jondurbin/bagel-34b",
        "model_family": "openrouter.ai",
        "cost_input": 0.003,
        "cost_output": 0.003
    },
    "openrouter.ai/jebcarter/psyfighter-13b": {
        "model_api_name": "jebcarter/psyfighter-13b",
        "model_family": "openrouter.ai",
        "cost_input": 0.001,
        "cost_output": 0.001
    },
    "openrouter.ai/koboldai/psyfighter-13b-2": {
        "model_api_name": "koboldai/psyfighter-13b-2",
        "model_family": "openrouter.ai",
        "cost_input": 0.001,
        "cost_output": 0.001
    },
    "openrouter.ai/neversleep/noromaid-mixtral-8x7b-instruct": {
        "model_api_name": "neversleep/noromaid-mixtral-8x7b-instruct",
        "model_family": "openrouter.ai",
        "cost_input": 0.003,
        "cost_output": 0.003
    },
    "openrouter.ai/nousresearch/nous-hermes-llama2-13b": {
        "model_api_name": "nousresearch/nous-hermes-llama2-13b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00015,
        "cost_output": 0.00015
    },
    "openrouter.ai/meta-llama/codellama-34b-instruct": {
        "model_api_name": "meta-llama/codellama-34b-instruct",
        "model_family": "openrouter.ai",
        "cost_input": 0.0004,
        "cost_output": 0.0004
    },
    "openrouter.ai/phind/phind-codellama-34b": {
        "model_api_name": "phind/phind-codellama-34b",
        "model_family": "openrouter.ai",
        "cost_input": 0.0004,
        "cost_output": 0.0004
    },
    "openrouter.ai/intel/neural-chat-7b": {
        "model_api_name": "intel/neural-chat-7b",
        "model_family": "openrouter.ai",
        "cost_input": 0.005,
        "cost_output": 0.005
    },
    "openrouter.ai/nousresearch/nous-hermes-2-mixtral-8x7b-dpo": {
        "model_api_name": "nousresearch/nous-hermes-2-mixtral-8x7b-dpo",
        "model_family": "openrouter.ai",
        "cost_input": 0.0003,
        "cost_output": 0.0003
    },
    "openrouter.ai/nousresearch/nous-hermes-2-mixtral-8x7b-sft": {
        "model_api_name": "nousresearch/nous-hermes-2-mixtral-8x7b-sft",
        "model_family": "openrouter.ai",
        "cost_input": 0.0003,
        "cost_output": 0.0003
    },
    "openrouter.ai/haotian-liu/llava-13b": {
        "model_api_name": "haotian-liu/llava-13b",
        "model_family": "openrouter.ai",
        "cost_input": 0.005,
        "cost_output": 0.005
    },
    "openrouter.ai/nousresearch/nous-hermes-2-vision-7b": {
        "model_api_name": "nousresearch/nous-hermes-2-vision-7b",
        "model_family": "openrouter.ai",
        "cost_input": 0.005,
        "cost_output": 0.005
    },
    "openrouter.ai/meta-llama/llama-2-13b-chat": {
        "model_api_name": "meta-llama/llama-2-13b-chat",
        "model_family": "openrouter.ai",
        "cost_input": 0.00015,
        "cost_output": 0.00015
    },
    "openrouter.ai/gryphe/mythomax-l2-13b": {
        "model_api_name": "gryphe/mythomax-l2-13b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00022,
        "cost_output": 0.00022
    },
    "openrouter.ai/nousresearch/nous-hermes-llama2-70b": {
        "model_api_name": "nousresearch/nous-hermes-llama2-70b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00081,
        "cost_output": 0.00081
    },
    "openrouter.ai/nousresearch/nous-capybara-7b": {
        "model_api_name": "nousresearch/nous-capybara-7b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00018,
        "cost_output": 0.00018
    },
    "openrouter.ai/codellama/codellama-70b-instruct": {
        "model_api_name": "codellama/codellama-70b-instruct",
        "model_family": "openrouter.ai",
        "cost_input": 0.00081,
        "cost_output": 0.00081
    },
    "openrouter.ai/teknium/openhermes-2-mistral-7b": {
        "model_api_name": "teknium/openhermes-2-mistral-7b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00018,
        "cost_output": 0.00018
    },
    "openrouter.ai/teknium/openhermes-2.5-mistral-7b": {
        "model_api_name": "teknium/openhermes-2.5-mistral-7b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00018,
        "cost_output": 0.00018
    },
    "openrouter.ai/undi95/remm-slerp-l2-13b": {
        "model_api_name": "undi95/remm-slerp-l2-13b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00027,
        "cost_output": 0.00027
    },
    "openrouter.ai/undi95/toppy-m-7b": {
        "model_api_name": "undi95/toppy-m-7b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00018,
        "cost_output": 0.00018
    },
    "openrouter.ai/openrouter/cinematika-7b": {
        "model_api_name": "openrouter/cinematika-7b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00018,
        "cost_output": 0.00018
    },
    "openrouter.ai/01-ai/yi-34b-chat": {
        "model_api_name": "01-ai/yi-34b-chat",
        "model_family": "openrouter.ai",
        "cost_input": 0.00072,
        "cost_output": 0.00072
    },
    "openrouter.ai/01-ai/yi-34b": {
        "model_api_name": "01-ai/yi-34b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00072,
        "cost_output": 0.00072
    },
    "openrouter.ai/01-ai/yi-6b": {
        "model_api_name": "01-ai/yi-6b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00013,
        "cost_output": 0.00013
    },
    "openrouter.ai/togethercomputer/stripedhyena-nous-7b": {
        "model_api_name": "togethercomputer/stripedhyena-nous-7b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00018,
        "cost_output": 0.00018
    },
    "openrouter.ai/togethercomputer/stripedhyena-hessian-7b": {
        "model_api_name": "togethercomputer/stripedhyena-hessian-7b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00018,
        "cost_output": 0.00018
    },
    "openrouter.ai/mistralai/mixtral-8x7b": {
        "model_api_name": "mistralai/mixtral-8x7b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00054,
        "cost_output": 0.00054
    },
    "openrouter.ai/nousresearch/nous-hermes-yi-34b": {
        "model_api_name": "nousresearch/nous-hermes-yi-34b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00072,
        "cost_output": 0.00072
    },
    "openrouter.ai/open-orca/mistral-7b-openorca": {
        "model_api_name": "open-orca/mistral-7b-openorca",
        "model_family": "openrouter.ai",
        "cost_input": 0.00014,
        "cost_output": 0.00014
    },
    "openrouter.ai/huggingfaceh4/zephyr-7b-beta": {
        "model_api_name": "huggingfaceh4/zephyr-7b-beta",
        "model_family": "openrouter.ai",
        "cost_input": 0.00014,
        "cost_output": 0.00014
    },
    "openrouter.ai/openai/gpt-3.5-turbo": {
        "model_api_name": "openai/gpt-3.5-turbo",
        "model_family": "openrouter.ai",
        "cost_input": 0.001,
        "cost_output": 0.002
    },
    "openrouter.ai/openai/gpt-3.5-turbo-0125": {
        "model_api_name": "openai/gpt-3.5-turbo-0125",
        "model_family": "openrouter.ai",
        "cost_input": 0.0005,
        "cost_output": 0.0015
    },
    "openrouter.ai/openai/gpt-3.5-turbo-1106": {
        "model_api_name": "openai/gpt-3.5-turbo-1106",
        "model_family": "openrouter.ai",
        "cost_input": 0.001,
        "cost_output": 0.002
    },
    "openrouter.ai/openai/gpt-3.5-turbo-0613": {
        "model_api_name": "openai/gpt-3.5-turbo-0613",
        "model_family": "openrouter.ai",
        "cost_input": 0.001,
        "cost_output": 0.002
    },
    "openrouter.ai/openai/gpt-3.5-turbo-0301": {
        "model_api_name": "openai/gpt-3.5-turbo-0301",
        "model_family": "openrouter.ai",
        "cost_input": 0.001,
        "cost_output": 0.002
    },
    "openrouter.ai/openai/gpt-3.5-turbo-16k": {
        "model_api_name": "openai/gpt-3.5-turbo-16k",
        "model_family": "openrouter.ai",
        "cost_input": 0.003,
        "cost_output": 0.004
    },
    "openrouter.ai/openai/gpt-4-turbo-preview": {
        "model_api_name": "openai/gpt-4-turbo-preview",
        "model_family": "openrouter.ai",
        "cost_input": 0.01,
        "cost_output": 0.03
    },
    "openrouter.ai/openai/gpt-4-1106-preview": {
        "model_api_name": "openai/gpt-4-1106-preview",
        "model_family": "openrouter.ai",
        "cost_input": 0.01,
        "cost_output": 0.03
    },
    "openrouter.ai/openai/gpt-4": {
        "model_api_name": "openai/gpt-4",
        "model_family": "openrouter.ai",
        "cost_input": 0.03,
        "cost_output": 0.06
    },
    "openrouter.ai/openai/gpt-4-0314": {
        "model_api_name": "openai/gpt-4-0314",
        "model_family": "openrouter.ai",
        "cost_input": 0.03,
        "cost_output": 0.06
    },
    "openrouter.ai/openai/gpt-4-32k": {
        "model_api_name": "openai/gpt-4-32k",
        "model_family": "openrouter.ai",
        "cost_input": 0.06,
        "cost_output": 0.12
    },
    "openrouter.ai/openai/gpt-4-32k-0314": {
        "model_api_name": "openai/gpt-4-32k-0314",
        "model_family": "openrouter.ai",
        "cost_input": 0.06,
        "cost_output": 0.12
    },
    "openrouter.ai/openai/gpt-4-vision-preview": {
        "model_api_name": "openai/gpt-4-vision-preview",
        "model_family": "openrouter.ai",
        "cost_input": 0.01,
        "cost_output": 0.03
    },
    "openrouter.ai/openai/gpt-3.5-turbo-instruct": {
        "model_api_name": "openai/gpt-3.5-turbo-instruct",
        "model_family": "openrouter.ai",
        "cost_input": 0.0015,
        "cost_output": 0.002
    },
    "openrouter.ai/google/palm-2-chat-bison": {
        "model_api_name": "google/palm-2-chat-bison",
        "model_family": "openrouter.ai",
        "cost_input": 0.00025,
        "cost_output": 0.0005
    },
    "openrouter.ai/google/palm-2-codechat-bison": {
        "model_api_name": "google/palm-2-codechat-bison",
        "model_family": "openrouter.ai",
        "cost_input": 0.00025,
        "cost_output": 0.0005
    },
    "openrouter.ai/google/palm-2-chat-bison-32k": {
        "model_api_name": "google/palm-2-chat-bison-32k",
        "model_family": "openrouter.ai",
        "cost_input": 0.00025,
        "cost_output": 0.0005
    },
    "openrouter.ai/google/palm-2-codechat-bison-32k": {
        "model_api_name": "google/palm-2-codechat-bison-32k",
        "model_family": "openrouter.ai",
        "cost_input": 0.00025,
        "cost_output": 0.0005
    },
    "openrouter.ai/google/gemini-pro": {
        "model_api_name": "google/gemini-pro",
        "model_family": "openrouter.ai",
        "cost_input": 0.00025,
        "cost_output": 0.0005
    },
    "openrouter.ai/google/gemini-pro-vision": {
        "model_api_name": "google/gemini-pro-vision",
        "model_family": "openrouter.ai",
        "cost_input": 0.00025,
        "cost_output": 0.0005
    },
    "openrouter.ai/perplexity/pplx-70b-online": {
        "model_api_name": "perplexity/pplx-70b-online",
        "model_family": "openrouter.ai",
        "cost_input": 0.0,
        "cost_output": 0.0028
    },
    "openrouter.ai/perplexity/pplx-7b-online": {
        "model_api_name": "perplexity/pplx-7b-online",
        "model_family": "openrouter.ai",
        "cost_input": 0.0,
        "cost_output": 0.00028
    },
    "openrouter.ai/perplexity/pplx-7b-chat": {
        "model_api_name": "perplexity/pplx-7b-chat",
        "model_family": "openrouter.ai",
        "cost_input": 7e-05,
        "cost_output": 0.00028
    },
    "openrouter.ai/perplexity/pplx-70b-chat": {
        "model_api_name": "perplexity/pplx-70b-chat",
        "model_family": "openrouter.ai",
        "cost_input": 0.0007,
        "cost_output": 0.0028
    },
    "openrouter.ai/meta-llama/llama-2-70b-chat": {
        "model_api_name": "meta-llama/llama-2-70b-chat",
        "model_family": "openrouter.ai",
        "cost_input": 0.0007,
        "cost_output": 0.0009
    },
    "openrouter.ai/jondurbin/airoboros-l2-70b": {
        "model_api_name": "jondurbin/airoboros-l2-70b",
        "model_family": "openrouter.ai",
        "cost_input": 0.0007,
        "cost_output": 0.0009
    },
    "openrouter.ai/austism/chronos-hermes-13b": {
        "model_api_name": "austism/chronos-hermes-13b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00022,
        "cost_output": 0.00022
    },
    "openrouter.ai/migtissera/synthia-70b": {
        "model_api_name": "migtissera/synthia-70b",
        "model_family": "openrouter.ai",
        "cost_input": 0.005,
        "cost_output": 0.005
    },
    "openrouter.ai/mistralai/mistral-7b-instruct": {
        "model_api_name": "mistralai/mistral-7b-instruct",
        "model_family": "openrouter.ai",
        "cost_input": 0.00013,
        "cost_output": 0.00013
    },
    "openrouter.ai/pygmalionai/mythalion-13b": {
        "model_api_name": "pygmalionai/mythalion-13b",
        "model_family": "openrouter.ai",
        "cost_input": 0.0015,
        "cost_output": 0.0015
    },
    "openrouter.ai/undi95/remm-slerp-l2-13b-6k": {
        "model_api_name": "undi95/remm-slerp-l2-13b-6k",
        "model_family": "openrouter.ai",
        "cost_input": 0.0015,
        "cost_output": 0.0015
    },
    "openrouter.ai/xwin-lm/xwin-lm-70b": {
        "model_api_name": "xwin-lm/xwin-lm-70b",
        "model_family": "openrouter.ai",
        "cost_input": 0.005,
        "cost_output": 0.005
    },
    "openrouter.ai/gryphe/mythomax-l2-13b-8k": {
        "model_api_name": "gryphe/mythomax-l2-13b-8k",
        "model_family": "openrouter.ai",
        "cost_input": 0.0015,
        "cost_output": 0.0015
    },
    "openrouter.ai/openchat/openchat-7b": {
        "model_api_name": "openchat/openchat-7b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00013,
        "cost_output": 0.00013
    },
    "openrouter.ai/alpindale/goliath-120b": {
        "model_api_name": "alpindale/goliath-120b",
        "model_family": "openrouter.ai",
        "cost_input": 0.0125,
        "cost_output": 0.0125
    },
    "openrouter.ai/lizpreciatior/lzlv-70b-fp16-hf": {
        "model_api_name": "lizpreciatior/lzlv-70b-fp16-hf",
        "model_family": "openrouter.ai",
        "cost_input": 0.0007,
        "cost_output": 0.0009
    },
    "openrouter.ai/neversleep/noromaid-20b": {
        "model_api_name": "neversleep/noromaid-20b",
        "model_family": "openrouter.ai",
        "cost_input": 0.003,
        "cost_output": 0.003
    },
    "openrouter.ai/gryphe/mythomist-7b": {
        "model_api_name": "gryphe/mythomist-7b",
        "model_family": "openrouter.ai",
        "cost_input": 0.0005,
        "cost_output": 0.0005
    },
    "openrouter.ai/mistralai/mixtral-8x7b-instruct": {
        "model_api_name": "mistralai/mixtral-8x7b-instruct",
        "model_family": "openrouter.ai",
        "cost_input": 0.00027,
        "cost_output": 0.00027
    },
    "openrouter.ai/cognitivecomputations/dolphin-mixtral-8x7b": {
        "model_api_name": "cognitivecomputations/dolphin-mixtral-8x7b",
        "model_family": "openrouter.ai",
        "cost_input": 0.00027,
        "cost_output": 0.00027
    },
    "openrouter.ai/rwkv/rwkv-5-world-3b": {
        "model_api_name": "rwkv/rwkv-5-world-3b",
        "model_family": "openrouter.ai",
        "cost_input": 0.0,
        "cost_output": 0.0
    },
    "openrouter.ai/recursal/rwkv-5-3b-ai-town": {
        "model_api_name": "recursal/rwkv-5-3b-ai-town",
        "model_family": "openrouter.ai",
        "cost_input": 0.0,
        "cost_output": 0.0
    },
    "openrouter.ai/recursal/eagle-7b": {
        "model_api_name": "recursal/eagle-7b",
        "model_family": "openrouter.ai",
        "cost_input": 0.0,
        "cost_output": 0.0
    },
    "openrouter.ai/anthropic/claude-2": {
        "model_api_name": "anthropic/claude-2",
        "model_family": "openrouter.ai",
        "cost_input": 0.008,
        "cost_output": 0.024
    },
    "openrouter.ai/anthropic/claude-2.1": {
        "model_api_name": "anthropic/claude-2.1",
        "model_family": "openrouter.ai",
        "cost_input": 0.008,
        "cost_output": 0.024
    },
    "openrouter.ai/anthropic/claude-2.0": {
        "model_api_name": "anthropic/claude-2.0",
        "model_family": "openrouter.ai",
        "cost_input": 0.008,
        "cost_output": 0.024
    },
    "openrouter.ai/anthropic/claude-instant-1": {
        "model_api_name": "anthropic/claude-instant-1",
        "model_family": "openrouter.ai",
        "cost_input": 0.0008,
        "cost_output": 0.0024
    },
    "openrouter.ai/anthropic/claude-instant-1.2": {
        "model_api_name": "anthropic/claude-instant-1.2",
        "model_family": "openrouter.ai",
        "cost_input": 0.0008,
        "cost_output": 0.0024
    },
    "openrouter.ai/anthropic/claude-1": {
        "model_api_name": "anthropic/claude-1",
        "model_family": "openrouter.ai",
        "cost_input": 0.008,
        "cost_output": 0.024
    },
    "openrouter.ai/anthropic/claude-1.2": {
        "model_api_name": "anthropic/claude-1.2",
        "model_family": "openrouter.ai",
        "cost_input": 0.008,
        "cost_output": 0.024
    },
    "openrouter.ai/anthropic/claude-instant-1.0": {
        "model_api_name": "anthropic/claude-instant-1.0",
        "model_family": "openrouter.ai",
        "cost_input": 0.0008,
        "cost_output": 0.0024
    },
    "openrouter.ai/anthropic/claude-instant-1.1": {
        "model_api_name": "anthropic/claude-instant-1.1",
        "model_family": "openrouter.ai",
        "cost_input": 0.0008,
        "cost_output": 0.0024
    },
    "openrouter.ai/anthropic/claude-2:beta": {
        "model_api_name": "anthropic/claude-2:beta",
        "model_family": "openrouter.ai",
        "cost_input": 0.008,
        "cost_output": 0.024
    },
    "openrouter.ai/anthropic/claude-2.1:beta": {
        "model_api_name": "anthropic/claude-2.1:beta",
        "model_family": "openrouter.ai",
        "cost_input": 0.008,
        "cost_output": 0.024
    },
    "openrouter.ai/anthropic/claude-2.0:beta": {
        "model_api_name": "anthropic/claude-2.0:beta",
        "model_family": "openrouter.ai",
        "cost_input": 0.008,
        "cost_output": 0.024
    },
    "openrouter.ai/anthropic/claude-instant-1:beta": {
        "model_api_name": "anthropic/claude-instant-1:beta",
        "model_family": "openrouter.ai",
        "cost_input": 0.0008,
        "cost_output": 0.0024
    },
    "openrouter.ai/huggingfaceh4/zephyr-7b-beta:free": {
        "model_api_name": "huggingfaceh4/zephyr-7b-beta:free",
        "model_family": "openrouter.ai",
        "cost_input": 0.0,
        "cost_output": 0.0
    },
    "openrouter.ai/openchat/openchat-7b:free": {
        "model_api_name": "openchat/openchat-7b:free",
        "model_family": "openrouter.ai",
        "cost_input": 0.0,
        "cost_output": 0.0
    },
    "openrouter.ai/mancer/weaver": {
        "model_api_name": "mancer/weaver",
        "model_family": "openrouter.ai",
        "cost_input": 0.0045,
        "cost_output": 0.0045
    },
    "openrouter.ai/mistralai/mistral-tiny": {
        "model_api_name": "mistralai/mistral-tiny",
        "model_family": "openrouter.ai",
        "cost_input": 0.00016,
        "cost_output": 0.00047
    },
    "openrouter.ai/mistralai/mistral-small": {
        "model_api_name": "mistralai/mistral-small",
        "model_family": "openrouter.ai",
        "cost_input": 0.00067,
        "cost_output": 0.002
    },
    "openrouter.ai/mistralai/mistral-medium": {
        "model_api_name": "mistralai/mistral-medium",
        "model_family": "openrouter.ai",
        "cost_input": 0.00278,
        "cost_output": 0.00833
    }
}
