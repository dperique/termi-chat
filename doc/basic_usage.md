# Simple usage with the basic_user.json

The [basic_user.json](../sample_conversations/basic_user.json) contains a simple and general
system prompt.  Tweak it as needed.  But it's meant to be general purpose and specific to the
user.  For day-to-day use, this is the one I use.

Here's a transcript:

```text
$ cd python/
python dperique$ ./termi-chat.py --load ../sample_conversations/basic_user.json --model gpt3.5 --names Cassy,Dennis
Context loaded from ../sample_conversations/basic_user.json.

Enter your command (type 'help' for options), or your conversation text:
Dennis, enter your text, then finish with a line containing only Ctrl-D and press Enter.

Do I need a bigger PC and GPU to run a 7B parameter LLM locally?
Processing...

Estimated tokens to be sent: 216
Press <ENTER> to send the message to the 'gpt-3.5-turbo-0125' assistant, or type 'cancel' to cancel.


--------------------------------------------------------------------------------
Response time: 2.14 seconds

Cassy:
Hey Dennis! Great to hear you're diving into Large Language Models (LLMs)! 🚀

For running a 7B parameter LLM like GPT-3 locally, you might need a more
powerful setup than your current one. A model of that size might require more
GPU memory and computational power than what your Nvidia RTX 3060 offers.

Given your current setup, you could definitely run smaller LLMs or even medium-
sized ones locally for experimentation and development. For the larger models
like GPT-3, you might want to consider cloud solutions like Runpod.io with
bigger GPUs or utilizing your Google Cloud credits for training.

If you're working with a 7B parameter LLM, I recommend leveraging cloud
resources for optimal performance without overburdening your local machine. Feel
free to ask if you need more guidance or have any specific requirements! 🤖💬


Enter your command (type 'help' for options), or your conversation text:
Dennis, enter your text, then finish with a line containing only Ctrl-D and press Enter.

How about a 3B parameter LLM? I'm 4-bit quant
Processing...

Estimated tokens to be sent: 435
Press <ENTER> to send the message to the 'gpt-3.5-turbo-0125' assistant, or type 'cancel' to cancel.


--------------------------------------------------------------------------------
Response time: 2.43 seconds

Cassy:
A 3B parameter LLM would still be quite demanding in terms of resources,
especially for fine-tuning and inference. Your current setup with the Nvidia RTX
3060 should be able to handle a 3B parameter model, but it might struggle with
larger batch sizes or more complex operations, especially if you are 4-bit
quantized.

For 4-bit quantization, you are trading off precision for faster computation,
which can be beneficial for certain applications but might require additional
tuning and optimization to achieve optimal performance.

I'd recommend starting with smaller batch sizes and experimenting with different
optimization strategies to find the right balance between performance and
resource efficiency on your local machine. For larger experiments or production-
level workloads, utilizing cloud resources like Runpod.io or your Google Cloud
credits would be beneficial.

Feel free to explore different configurations and optimizations to get the best
out of your current setup! If you need assistance with specific techniques or
tools for quantization and optimization, just let me know! 🤖🔧


Enter your command (type 'help' for options), or your conversation text:
Dennis, enter your text, then finish with a line containing only Ctrl-D and press Enter.

I'm just using inference
Processing...

Estimated tokens to be sent: 716
Press <ENTER> to send the message to the 'gpt-3.5-turbo-0125' assistant, or type 'cancel' to cancel.


--------------------------------------------------------------------------------
Response time: 2.05 seconds

Cassy:
If you're focusing solely on inference for a 3B parameter LLM without the need
for training, your current setup with the Nvidia RTX 3060 should be capable of
handling it, especially for smaller batch sizes.

Inference typically requires less computational resources compared to training,
so running a pre-trained 3B parameter LLM for inference on your local machine
should be feasible.

Just ensure you optimize your inference setup by fine-tuning batch sizes, input
sequences, and other hyperparameters to maximize performance within the
constraints of your GPU. Utilizing tools like TensorRT for GPU acceleration can
also help improve inference speed and efficiency.

For larger scale inferences or if you need to batch process a substantial amount
of data, leveraging cloud solutions like Runpod.io with bigger GPUs or your
Google Cloud credits can provide additional performance benefits.

If you encounter any specific challenges or performance bottlenecks during the
inference process, feel free to reach out for more detailed guidance! Happy
experimenting with LLM inference on your local setup! 🚀💻


Enter your command (type 'help' for options), or your conversation text:
Dennis, enter your text, then finish with a line containing only Ctrl-D and press Enter.

quit
Processing...

You have unsaved changes. Please save your context before quitting.

Enter your command (type 'help' for options), or your conversation text:
Dennis, enter your text, then finish with a line containing only Ctrl-D and press Enter.

save
Processing...

Enter filename to save the context: running_llms_conversation.json
Context saved to running_llms_conversation.json.

Enter your command (type 'help' for options), or your conversation text:
Dennis, enter your text, then finish with a line containing only Ctrl-D and press Enter.

quit
Processing...

Goodbye!
```

Once you save the conversation, you can edit it (if you want) and then load it again using the `--load` option later.
