import streamlit as st
import os
from poem import PoemManager
from images import UserVoteManager

curr_dir = os.path.dirname(os.path.abspath(__file__))

VOTE_PATH = os.path.join(curr_dir, "../data/votes.tsv")
USER_VOTE_PATH = os.path.join(curr_dir, "../data/user_votes.tsv")
IMAGE_DIR = os.path.join(curr_dir, "../static/images")

st.set_page_config("Demo: User Manager")
st.title("User Manager")

user_vote_manager = UserVoteManager(VOTE_PATH, USER_VOTE_PATH, IMAGE_DIR)
users = user_vote_manager.get_existing_users()

st.header("User and Vote Statistics")

st.subheader("User Voting Progress")
voting_count = (user_vote_manager._user_votes > 0).sum().astype(int)
for user in users:
    st.metric(user, f"{voting_count[user]} / {len(user_vote_manager._user_votes)}")

st.header("Add new user widget")

user_index = len(users)
with st.form(f"new_user_{user_index}"):
    new_user = st.text_input("Name", key=f"name_{user_index}")
    available = bool(new_user)
    if new_user in users:
        st.error("User already exist, please create a new one.")
        available = False

    submitted = st.form_submit_button("Add", type="primary", disabled=not available)

    if submitted:
        if user_vote_manager.initial_new_user(new_user):
            # If success
            user_vote_manager.save_votes()
            st.rerun()
