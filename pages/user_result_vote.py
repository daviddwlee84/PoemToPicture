import pandas as pd
import streamlit as st
import os
from poem import PoemManager
from images import UserVoteManager

curr_dir = os.path.dirname(os.path.abspath(__file__))

VOTE_PATH = os.path.join(curr_dir, "../data/votes.tsv")
USER_VOTE_PATH = os.path.join(curr_dir, "../data/user_votes.tsv")
IMAGE_DIR = os.path.join(curr_dir, "../static/images")
POEM_PATH = os.path.join(curr_dir, "../data/poems.tsv")

st.set_page_config("Demo: User Image Result Voting")
st.title("User Image Result Voting")

poem_manager = PoemManager(POEM_PATH)
user_vote_manager = UserVoteManager(VOTE_PATH, USER_VOTE_PATH, IMAGE_DIR)

if "changed" not in st.session_state:
    st.session_state["changed"] = False


def on_change():
    st.session_state["changed"] = True


vote_data = (
    user_vote_manager.get_joined_data()
)  # .drop('image_file', axis=1).rename({'streamlit_image_file': 'image_file'})

vote_data["poem_content"] = (
    vote_data["poem_id"].astype(int).apply(lambda x: poem_manager.get_by_id(x).content)
)

users = user_vote_manager.get_existing_users()

column_config = {
    "id": "index",
    "poem_id": st.column_config.NumberColumn("poem id"),
    "poem_name": st.column_config.TextColumn("title"),
    "poem_content": st.column_config.TextColumn("content"),
    "prompt_name": st.column_config.TextColumn("prompt name"),
    "version": st.column_config.TextColumn("image version"),
    "streamlit_image_file": st.column_config.ImageColumn("Preview Image"),
}
for user in users:
    column_config[user] = st.column_config.NumberColumn(
        f"{user}'s rating",
        help=f"How much do {user} like this image (1-5)?",
        min_value=1,
        max_value=5,
        step=1,
        format="%d ⭐",
    )

edited_vote_data = st.data_editor(
    vote_data[
        [
            "poem_id",
            "poem_name",
            "poem_content",
            "prompt_name",
            "version",
            "streamlit_image_file",
        ]
        + users
    ].sort_values(by=["poem_id", "prompt_name", "version"]),
    column_config=column_config,
    on_change=on_change,
    disabled=[
        "id",
        "poem_id",
        "poem_name",
        "poem_content",
        "prompt_name",
        "version",
        "streamlist_image_file",
    ],
)

if st.session_state["changed"]:
    user_vote_manager.update_user_votes(edited_vote_data, save=True)
    st.session_state["changed"] = False
    st.rerun()

# TODO: select users

# TODO
# https://docs.streamlit.io/library/api-reference/data/st.metric
# st.subheader("Average vote :star: for each prompt type")
# for prompt_name, df in vote_data.groupby("prompt_name"):
#     voted_df = df[df["vote"] != 0]
#     if voted_df.empty:
#         st.metric(prompt_name, "Haven't voted yet")
#         st.caption(f"Total image of prompt {prompt_name}:\t{len(df)}")
#         # https://docs.streamlit.io/library/api-reference/charts/st.bar_chart
#     else:
#         st.metric(prompt_name, f'{voted_df["vote"].mean():.1f} / 5')
#         st.caption(
#             f"Voted images versus total for prompt {prompt_name}:\t{len(voted_df)} / {len(df)}"
#         )
#         st.bar_chart(pd.Series({i: (voted_df["vote"] == i).sum() for i in range(1, 6)}))
