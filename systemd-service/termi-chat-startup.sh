#!/bin/bash
source /home/some-user/anaconda3/etc/profile.d/conda.sh
conda activate llama3-fine-tune
streamlit run --browser.gatherUsageStats false --server.port 8501 --theme.base dark /some-path/termi-chat/python/sl_TermChat.py conversation1

