from typing import Dict, Union, Optional
import streamlit as st
import pandas as pd

# TODO: add items to table
from images import ImageVoteManager

# TODO: check poem number and title match
from poem import PoemManager
import os
from PIL import Image

st.set_page_config("Demo: Import Images")
st.title("Import Images")

st.caption(
    "Expected the file naming logic is `{poem_id}_{poem_name}_{prompt_name}_{version}.png`. Please follow the rule otherwise the image will be ignore."
)

# https://docs.streamlit.io/library/api-reference/widgets/st.file_uploader
files = st.file_uploader("Upload Image(s)", type="png", accept_multiple_files=True)

file_mapping = {file.name: Image.open(file) for file in files}


def filename_parser(raw_filename: str) -> Optional[Dict[str, Union[int, str]]]:
    """
    If invalid then return None
    """
    try:
        raw_filename, _ = raw_filename.rsplit(".", 1)  # remove extension
        poem_id, poem_name, raw_filename = raw_filename.split("_", 2)
        prompt_name, version = raw_filename.rsplit("_", 1)
        return {
            "poem_id": int(poem_id),
            "poem_name": poem_name,
            "prompt_name": prompt_name,
            "version": version,
        }
    except:
        return None


with st.expander("Image Preview"):
    for filename, image in file_mapping.items():
        st.image(image, filename)

with st.expander("Version Preview"):
    st.write([{filename: filename_parser(filename)} for filename in file_mapping])
