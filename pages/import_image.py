from typing import Dict, Union, Optional
import streamlit as st
import pandas as pd
from stqdm import stqdm

from images import ImageVoteManager, UserVoteManager

# TODO: check poem number and title match
from poem import PoemManager
import os
from PIL import Image

curr_dir = os.path.dirname(os.path.abspath(__file__))

st.set_page_config("Demo: Import Images")
st.title("Import Images")

st.caption(
    "Expected the file naming logic is `{poem_id}_{poem_name}_{prompt_name}_{version}.png`. Please follow the rule otherwise the image will be ignore."
)

VOTE_PATH = os.path.join(curr_dir, "../data/votes.tsv")
USER_VOTE_PATH = os.path.join(curr_dir, "../data/user_votes.tsv")
IMAGE_DIR = os.path.join(curr_dir, "../static/images")
POEM_PATH = os.path.join(curr_dir, "../data/poems.tsv")

image_vote_manager = ImageVoteManager(VOTE_PATH, IMAGE_DIR)
poem_manger = PoemManager(POEM_PATH)

# https://docs.streamlit.io/library/api-reference/widgets/st.file_uploader
files = st.file_uploader(
    "Upload Image(s)",
    type="png",
    accept_multiple_files=True,
    key=f"uploader_{len(image_vote_manager)}",
)

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


def path_generator(file_detail: Dict[str, Union[int, str]], image_dir: str):
    return os.path.join(
        image_dir,
        str(file_detail["poem_id"])
        + "_"
        + file_detail["poem_name"]
        + "_"
        + file_detail["prompt_name"]
        + "_"
        + file_detail["version"]
        + ".png",
    )


with st.expander("Image Preview"):
    for filename, image in file_mapping.items():
        st.image(image, filename)

with st.expander("Version Preview"):
    st.write([{filename: filename_parser(filename)} for filename in file_mapping])

# TODO: what if there are duplicate files..?

invalid_files = set()
image_paths = {}
image_details = []
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

    image_paths[filename] = path_generator(file_detail, IMAGE_DIR)
    image_details.append(file_detail)

if not invalid_files:
    st.success(
        f"All {len(file_mapping)} image{'s' if len(file_mapping) > 1 else ''} are valid!"
    )
else:
    st.success(
        f"Found {len(image_paths)} valid image{'s' if len(image_paths) > 1 else ''}."
    )


st.subheader("Table Preview")
st.dataframe(pd.DataFrame(image_details))


with st.form("import"):
    override = st.checkbox("Override if exist", value=False)
    submit = st.form_submit_button("Submit")

    if submit:
        for filename, path in stqdm(image_paths.items(), desc="Importing Images"):
            if os.path.exists(path):
                if not override:
                    st.toast(f"Found existing image {path}. Skipped.")
                    continue
                else:
                    st.toast(f"Override existing image {path}.")

            file_mapping[filename].save(path)
            # with open(path, "wb") as image_file:
            #     image_file.write()

            # TODO: use cache
            image_vote_manager.append_new_index(**filename_parser(filename))

        image_vote_manager.save()
        # NOTE: This is used to update user vote table
        UserVoteManager(VOTE_PATH, USER_VOTE_PATH, IMAGE_DIR)
