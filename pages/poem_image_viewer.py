import streamlit as st
from images import ImageVoteManager
from poem import PoemManager
import os
from PIL import Image

curr_dir = os.path.dirname(os.path.abspath(__file__))

st.title("Poem Image Viewer")

image_vote_manager = ImageVoteManager(
    os.path.join(curr_dir, "../data/votes.tsv"),
    os.path.join(curr_dir, "../static/images"),
)
poem_manager = PoemManager(os.path.join(curr_dir, "../data/poems.tsv"))

poem_index = st.selectbox(
    "Select Poem",
    poem_manager._data.index,
    format_func=lambda x: f'{poem_manager._data.loc[x]["id"]} - {poem_manager._data.loc[x]["author"]} - {poem_manager._data.loc[x]["title"]}',
)

poem = poem_manager[poem_index]
prettify_content = poem.content.replace("，", "，\n").replace("。", "。\n")

st.subheader(poem.title)
st.caption(f"Author: {poem.author}")
st.caption(f"Dynasty: {poem.dynasty}")
st.text(prettify_content)

images = image_vote_manager.get_images_by_id(poem.id)
for prompt_name, df in images.groupby("prompt_name"):
    st.subheader(f"{prompt_name} Result")
    for i, row in df.iterrows():
        st.image(Image.open(row["image_file"]), caption=row["version"])
