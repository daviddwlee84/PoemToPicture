import streamlit as st
from poem import PoemManager
from prompts import PromptManager
from images import ImageVoteManager
from openai.error import OpenAIError
from inference import Pipeline, OpenAIInference, AzureInference
import os
from PIL import Image
from dotenv import load_dotenv

curr_dir = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(curr_dir, "../.env"))

st.set_page_config("Demo: Real-time Inference")
st.title("Real-time Inference")

api_version = st.selectbox("API Version", ["OpenAI", "Azure"], index=1)
# API_VERSION: Literal["OpenAI", "Azure"] = "Azure"
# st.caption(
#     f"You are now using {api_version} API. (modify this in `pages/inference_poem.py`)"
# )

image_vote_manager = ImageVoteManager(
    os.path.join(curr_dir, "../data/votes.tsv"),
    os.path.join(curr_dir, "../static/images"),
)
prompt_manager = PromptManager(os.path.join(curr_dir, "../data/prompts"))
poem_manager = PoemManager(os.path.join(curr_dir, "../data/poems.tsv"))

if api_version == "OpenAI":
    if not os.getenv("OPENAI_API_KEY"):
        st.error("OpenAI API Key not found. Please check your `.env`.")
        st.stop()
    api = OpenAIInference(os.getenv("OPENAI_API_KEY"))
else:
    if any(
        [
            os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME") is None,
            os.getenv("AZURE_OPENAI_ENDPOINT") is None,
            os.getenv("AZURE_OPENAI_KEY") is None,
            os.getenv("AZURE_OPENAI_VERSION") is None,
        ]
    ):
        st.error("Azure OpenAI API Key not found. Please check your `.env`.")
        st.stop()
    api = AzureInference(
        os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        os.getenv("AZURE_OPENAI_ENDPOINT"),
        os.getenv("AZURE_OPENAI_KEY"),
        os.getenv("AZURE_OPENAI_VERSION"),
    )

pipeline = Pipeline(image_vote_manager, api)

poem_index = st.selectbox(
    "Select Poem",
    poem_manager._data.index,
    format_func=lambda x: f'{poem_manager._data.loc[x]["id"]} - {poem_manager._data.loc[x]["author"]} - {poem_manager._data.loc[x]["title"]}',
)

poem = poem_manager[poem_index]

prompt = st.selectbox(
    "Select Prompt",
    prompt_manager._data,
    format_func=lambda x: x.name,
)

with st.expander("Raw Selected Object"):
    st.write(poem)
    st.write(prompt)

new_file_path = image_vote_manager.get_new_file_path(poem, prompt, update_data=False)
st.text(f"New file will be generated at {new_file_path}")

with st.expander("Existing Images for Poem-Prompt pair"):
    images = image_vote_manager.get_images_by_poem_prompt(poem, prompt)
    st.write(images)
    if images.empty:
        st.text("No existing images")
    else:
        st.text("Found existing images")
        # https://docs.streamlit.io/library/api-reference/media/st.image
        st.image(
            [Image.open(image_path) for image_path in images["image_file"]],
            images["version"].to_list(),
        )


# https://docs.streamlit.io/library/api-reference/control-flow/st.form
with st.form("inference"):
    st.write("Inference")
    # st.subheader("Poem and Prompt")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"""### {poem.id} - {poem.title} - {poem.author}

            {poem.content}
        """
        )
    with col2:
        st.write(
            {key: value for key, value in prompt.to_dict().items() if value is not None}
        )

    temperature = st.number_input(
        "Temperature", min_value=0.0, max_value=2.0, value=0.5, step=0.1
    )
    # Every form must have a submit button.
    # https://docs.streamlit.io/library/api-reference/control-flow/st.form_submit_button
    submitted = st.form_submit_button("Submit", type="primary")

    if submitted:
        # https://docs.streamlit.io/library/api-reference/status/st.spinner
        with st.spinner():
            try:
                (image_url, image_path) = pipeline(
                    prompt, poem, temperature=temperature
                )
            except OpenAIError as error:
                st.toast(f"Poem {poem} has an OpenAI error {error}", icon="⚠️")
            st.image(image_url)
            st.caption("Note that new image rending might be slow. Please wait :).")
