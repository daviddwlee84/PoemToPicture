import streamlit as st
import sys
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(curr_dir, ".."))


st.set_page_config(
    page_title="AI School Project 60",
    page_icon="👋",
)

st.write("# Welcome to Demo of Microsoft AI School 2023 Project 60! 👋")

st.sidebar.title("Functionality Explanation")
st.sidebar.markdown(
    """
- `batch inference`: Batch inference with selected prompt on all poems
- `import image`: Import image with formatted filename for voting
- `inference poem`: Real-time inference from combination of poem and prompt
- `poem image viewer`: View selected poem with processed images
- `poem manager`: View and add new poem
- `prompt manager`: View and add new prompt
- `result vote`: Vote generated results and show statistics
- `user manager`: View user voting progress and add new user
- `user result vote`: Vote generated results by user
"""
)

st.markdown(
    """
    ## Introduction

    TODO

    ## Motivation

    ## Links
    
    - Our repository: TODO
"""
)
