import streamlit as st
from openai.error import OpenAIError
from poem import PoemManager
from prompts import PromptManager
from images import ImageVoteManager
from inference import Pipeline, OpenAIInference, AzureInference
import os
from stqdm import stqdm
from dotenv import load_dotenv
from collections import defaultdict

curr_dir = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(curr_dir, "../.env"))

st.set_page_config("Demo: Batch Inference")
st.title("Batch Inference")

api_version = st.selectbox("API Version", ["OpenAI", "Azure"], index=1)


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


prompt = st.selectbox(
    "Select Prompt",
    prompt_manager._data,
    format_func=lambda x: x.name,
)

# https://docs.streamlit.io/library/api-reference/control-flow/st.form
with st.form("inference"):
    st.write("Batch Inference")
    col1, col2 = st.columns(2)

    with col1:
        temperature = st.number_input(
            "Temperature", min_value=0.0, max_value=2.0, value=0.5, step=0.1
        )
        n = st.number_input("Variations (n)", min_value=1, value=1, step=1)
    with col2:
        st.write(
            {key: value for key, value in prompt.to_dict().items() if value is not None}
        )

    submitted = st.form_submit_button("Submit", type="primary")

    if submitted:
        # TODO: make this multi-processing
        with st.spinner():
            results = defaultdict(list)
            # Debug
            # for poem in stqdm(list(poem_manager)[-10:], desc="Processing poem"):
            for poem in stqdm(poem_manager, desc="Processing poem"):
                for _ in range(n):
                    try:
                        (image_url, image_path) = pipeline(
                            prompt, poem, temperature=temperature
                        )
                        results[f"{poem.id}. {poem.title}"].append(
                            (image_url, image_path)
                        )
                    except OpenAIError as error:
                        st.toast(f"Poem {poem} has an OpenAI error {error}", icon="⚠️")

        with st.expander("Generated Image"):
            for title, images in results.items():
                st.text(title)
                for image_url, image_path in images:
                    filename = os.path.basename(image_path)
                    st.image(image_url, filename)
