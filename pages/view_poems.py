import streamlit as st
from poem import PoemManager
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))

st.title("Poems")

poem_manager = PoemManager(os.path.join(curr_dir, "../data/poems.tsv"))

st.dataframe(poem_manager._data.set_index("id"), use_container_width=True)

# TODO: able to edit and add poem here
