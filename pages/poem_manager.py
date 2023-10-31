import streamlit as st
from poem import PoemManager, Poem
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))

st.set_page_config("Demo: Poem Manager")
st.title("Poems")

poem_manger = PoemManager(os.path.join(curr_dir, "../data/poems.tsv"))

st.dataframe(poem_manger._data.set_index("id"), use_container_width=True)

st.header("Add new poem widget")

can_submit = True

st.write(f"New poem will be id {len(poem_manger)}")
# NOTE: "key" is for refresh content
index = len(poem_manger)
title = st.text_input("Title", key=f"title_{index}")
if not title:
    st.error("Title is a must have!")
    can_submit = False
if poem_manger.get_by_title(title):
    st.warning("Poem with this title has already exist.")
author = st.text_input("Author", key=f"author_{index}")
dynasty = st.text_input("Dynasty", key=f"dynasty_{index}")
content = st.text_area("Content", key=f"content_{index}")
if not content:
    st.error("Content is a must have!")
    can_submit = False
if poem_manger.get_by_content(content):
    st.warning("Poem with this content has already exist.")

# StreamlitAPIException: Values for st.button, st.download_button, st.file_uploader, st.data_editor, st.chat_input, and st.form cannot be set using st.session_state.
submitted = st.button(
    "Add", type="primary", key=f"button_{index}", disabled=not can_submit
)

if submitted:
    new_poem = Poem(index, title, author, dynasty, content)
    poem_manger.append(new_poem)
    poem_manger.save()
    st.rerun()
