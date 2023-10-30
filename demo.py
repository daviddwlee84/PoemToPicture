import streamlit as st
import sys
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.append(os.path.join(curr_dir, ".."))


st.set_page_config(
    page_title="AI School Project 60",
    page_icon="👋",
)

st.write("# Welcome to Demo of AI School Project 60! 👋")

st.sidebar.success("Select a demo above.")

st.markdown(
    """
    ## Introduction

    TODO

    ## Motivation

    ## Links
    
    - Our repository: TODO
"""
)
