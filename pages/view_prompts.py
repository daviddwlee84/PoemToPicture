import streamlit as st
from prompts import PromptManager
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))

st.title("Prompts")

prompt_manager = PromptManager(os.path.join(curr_dir, "../data/prompts"))

prompts = []
for prompt in prompt_manager._data:
    prompt_dict = prompt.to_dict()
    name = prompt_dict.pop("name")
    prompts.append({name: prompt_dict})

st.write(prompts)

# TODO: able to edit and add prompt here
