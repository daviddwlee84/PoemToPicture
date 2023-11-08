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

# TODO: what if there are duplicate files..?

curr_dir = os.path.dirname(os.path.abspath(__file__))
poem_manger = PoemManager(os.path.join(curr_dir, "../data/poems.tsv"))

invalid_files = set()
for filename in file_mapping:
    if (file_detail := filename_parser(filename)) is None:
        st.warning(f"Invalid filename ({filename}) found. Will be skipped.")
        invalid_files.add(filename)
        continue

    if (poem := poem_manger.get_by_id(file_detail["poem_id"])) is None:
        st.warning(
            f"Invalid poem id ({file_detail['poem_id']}) found. Will be skipped."
        )
        invalid_files.add(filename)
        continue

    if poem.title != file_detail["poem_name"]:
        st.warning(
            f"Poem id is not matched with the title ({file_detail['poem_name']}). Will be skipped."
        )
        invalid_files.add(filename)
        continue

if not invalid_files:
    st.success(
        f"All {len(file_mapping)} image{'s' if len(file_mapping) > 1 else ''} are valid!"
    )
else:
    st.success(
        f"Found {len(file_mapping) - len(invalid_files)} valid image{'s' if len(file_mapping) - len(invalid_files) > 1 else ''}."
    )
