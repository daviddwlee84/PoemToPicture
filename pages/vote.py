import pandas as pd
import streamlit as st
import os

curr_dir = os.path.dirname(os.path.abspath(__file__))

VOTE_PATH = os.path.join(curr_dir, "../data/votes.tsv")

if "changed" not in st.session_state:
    st.session_state["changed"] = False


def on_change():
    st.session_state["changed"] = True


vote_data = pd.read_csv(
    VOTE_PATH,
    sep="\t",
    index_col=0,
    dtype={"poem_id": int, "prompt_name": str, "version": str, "vote": int},
)

edited_vote_data = st.data_editor(
    vote_data,
    column_config={
        "id": "index",
        "poem_id": st.column_config.NumberColumn("poem id"),
        "poem_name": st.column_config.TextColumn("poem name"),
        "version": st.column_config.TextColumn("image version"),
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
    disabled=["id", "poem_id", "poem_name", "prompt_name", "version"],
)

if st.session_state["changed"]:
    edited_vote_data.to_csv(VOTE_PATH, sep="\t")
    st.session_state["changed"] = False
    st.rerun()
