import pandas as pd
import streamlit as st
import os
from poem import PoemManager

curr_dir = os.path.dirname(os.path.abspath(__file__))

VOTE_PATH = os.path.join(curr_dir, "../data/votes.tsv")
POEM_PATH = os.path.join(curr_dir, "../data/poems.tsv")

poem_manager = PoemManager(POEM_PATH)

st.title("Voting")

if "changed" not in st.session_state:
    st.session_state["changed"] = False


def on_change():
    st.session_state["changed"] = True


vote_data = pd.read_csv(
    VOTE_PATH,
    sep="\t",
    index_col=0,
    dtype={
        "poem_id": str,
        "poem_name": str,
        "prompt_name": str,
        "version": str,
        "vote": int,
    },
)

vote_data["image_file"] = (
    # os.path.join(curr_dir, "../data/images/")
    "app/static/images/"
    + vote_data["poem_id"]
    + "_"
    + vote_data["poem_name"]
    + "_"
    + vote_data["prompt_name"]
    + "_"
    + vote_data["version"]
    + ".png"
)

vote_data["poem_content"] = (
    vote_data["poem_id"].astype(int).apply(lambda x: poem_manager.get_by_id(x).content)
)

edited_vote_data = st.data_editor(
    vote_data[
        [
            "poem_id",
            "poem_name",
            "poem_content",
            "prompt_name",
            "version",
            "image_file",
            "vote",
        ]
    ],
    column_config={
        "id": "index",
        "poem_id": st.column_config.NumberColumn("poem id"),
        "poem_name": st.column_config.TextColumn("title"),
        "poem_content": st.column_config.TextColumn("content"),
        "prompt_name": st.column_config.TextColumn("prompt name"),
        "version": st.column_config.TextColumn("image version"),
        "image_file": st.column_config.ImageColumn("Preview Image"),
        "vote": st.column_config.NumberColumn(
            "rating",
            help="How much do you like this image (1-5)?",
            min_value=1,
            max_value=5,
            step=1,
            format="%d ⭐",
        ),
    },
    on_change=on_change,
    disabled=[
        "id",
        "poem_id",
        "poem_name",
        "poem_content",
        "prompt_name",
        "version",
        "image_file",
    ],
)

if st.session_state["changed"]:
    edited_vote_data[["poem_id", "poem_name", "prompt_name", "version", "vote"]].to_csv(
        VOTE_PATH, sep="\t"
    )
    st.session_state["changed"] = False
    st.rerun()
