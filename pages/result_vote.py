import pandas as pd
import streamlit as st
import os
from poem import PoemManager

curr_dir = os.path.dirname(os.path.abspath(__file__))

VOTE_PATH = os.path.join(curr_dir, "../data/votes.tsv")
POEM_PATH = os.path.join(curr_dir, "../data/poems.tsv")

poem_manager = PoemManager(POEM_PATH)

st.set_page_config("Demo: Image Result Voting (Deprecated)")
st.title("Image Result Voting (Deprecated)")

if "changed" not in st.session_state:
    st.session_state["changed"] = False


def on_change():
    st.session_state["changed"] = True


vote_data = pd.read_csv(
    VOTE_PATH,
    sep="\t",
    index_col=0,
    dtype={
        "poem_id": int,
        "poem_name": str,
        "prompt_name": str,
        "version": str,
        "vote": int,
    },
)

vote_data["image_file"] = (
    # os.path.join(curr_dir, "../data/images/")
    "app/static/images/"
    + vote_data["poem_id"].astype(str)
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
    ].sort_values(by=["poem_id", "prompt_name", "version"]),
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
    edited_vote_data[
        ["poem_id", "poem_name", "prompt_name", "version", "vote"]
    ].sort_index().to_csv(VOTE_PATH, sep="\t")
    st.session_state["changed"] = False
    st.rerun()

# https://docs.streamlit.io/library/api-reference/data/st.metric
st.subheader("Average vote :star: for each prompt type")
for prompt_name, df in vote_data.groupby("prompt_name"):
    voted_df = df[df["vote"] != 0]
    if voted_df.empty:
        st.metric(prompt_name, "Haven't voted yet")
        st.caption(f"Total image of prompt {prompt_name}:\t{len(df)}")
        # https://docs.streamlit.io/library/api-reference/charts/st.bar_chart
    else:
        st.metric(prompt_name, f'{voted_df["vote"].mean():.1f} / 5')
        st.caption(
            f"Voted images versus total for prompt {prompt_name}:\t{len(voted_df)} / {len(df)}"
        )
        st.bar_chart(pd.Series({i: (voted_df["vote"] == i).sum() for i in range(1, 6)}))
