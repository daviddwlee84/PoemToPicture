import streamlit as st
from prompts import PromptManager, Prompt
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))

st.set_page_config("Demo: Prompt Manager")
st.title("Prompts")

prompt_manager = PromptManager(os.path.join(curr_dir, "../data/prompts"))

prompts = []
for prompt in prompt_manager._data:
    prompt_dict = prompt.to_dict()
    name = prompt_dict.pop("name")
    prompts.append({name: prompt_dict})

st.write(prompts)

st.header("Add new prompt widget")

can_submit = True

index = len(prompt_manager)
name = st.text_input("Prompt Name", key=f"name_{index}")
if not name:
    st.error("Prompt name is a must have!")
    can_submit = False
if prompt_manager.get_by_name(name):
    st.warning("Prompt with this title has already exist.")
    can_submit = False
system = st.text_area(
    "System Prompt (to initial ChatGPT context)", key=f"system_{index}"
)
chatgpt = st.text_area(
    "User Prompt (to guide ChatGPT to generate Dall-E prompt)", key=f"chatgpt_{index}"
)
dalle = st.text_area(
    "Dall-E Prompt (use `{output}` to inherit output from ChatGPT if needed)",
    key=f"dalle_{index}",
)
if not dalle:
    st.error("Dall-E prompt is a must have!")
    can_submit = False
if "{output}" in dalle and (not system or not chatgpt):
    st.error(
        "You must given ChatGPT's system and user prompt to use `{output}` placeholder."
    )
    can_submit = False

submitted = st.button(
    "Add", type="primary", key=f"button_{index}", disabled=not can_submit
)

if submitted:
    new_prompt = Prompt(
        name, dalle, system if system else None, chatgpt if chatgpt else None
    )
    prompt_manager.append(new_prompt, save=True)
    st.rerun()
