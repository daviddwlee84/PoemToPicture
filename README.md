# Poem To Picture

Using LLM to create image from poem

## Getting Started

```powershell
pip install -r .\requirements.txt
```

```powershell
cp example.env .env
# Set your API keys
```

```powershell
streamlit run demo.py
# or
.\demo.ps1
```

> NOTE:
> 
> - You don't have to restart the server if you change the page code or source data
> - You have to restart the server if you change dependencies (i.e. imported library)

## Resources

- [Best Practices for API Key Safety | OpenAI Help Center](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety)
- [Quickstart tutorial - OpenAI API](https://platform.openai.com/docs/quickstart?context=python)

### Large Language Model

- [langchain-ai/langchain: ⚡ Building applications with LLMs through composability ⚡](https://github.com/langchain-ai/langchain)

### Image Generation

- LangChain
  - [Dall-E Image Generator | 🦜️🔗 Langchain](https://python.langchain.com/docs/integrations/tools/dalle_image_generator)
- OpenAI
  - [Image generation - OpenAI API](https://platform.openai.com/docs/guides/images/introduction?context=python)
- OctoAI
  - [Stable Diffusion 1.5 on OctoAI is the world's fastest SD model | OctoML](https://octoml.ai/models/stable-diffusion/)
- Bing Image Creator
  - [Image Creator from Microsoft Bing](https://www.bing.com/images/create)
  - [Bing Image Creator](https://www.microsoft.com/en-us/edge/features/image-creator?form=MT00D8)

### User Interface

- [How to Use Flask-SQLAlchemy to Interact with Databases in a Flask Application | DigitalOcean](https://www.digitalocean.com/community/tutorials/how-to-use-flask-sqlalchemy-to-interact-with-databases-in-a-flask-application)
- Streamlit
  - [PablocFonseca/streamlit-aggrid: Implementation of Ag-Grid component for Streamlit](https://github.com/PablocFonseca/streamlit-aggrid)
  - [st.data_editor - Streamlit Docs](https://docs.streamlit.io/library/api-reference/data/st.data_editor#configuring-columns)
  - [st.column_config - Streamlit Docs](https://docs.streamlit.io/library/api-reference/data/st.column_config)
  - [Static file serving - Streamlit Docs](https://docs.streamlit.io/library/advanced-features/static-file-serving)
  - [Configuration - Streamlit Docs](https://docs.streamlit.io/library/advanced-features/configuration)
  - [Introducing multipage apps! 📄](https://blog.streamlit.io/introducing-multipage-apps/)
  - [Button behavior and examples - Streamlit Docs](https://docs.streamlit.io/library/advanced-features/button-behavior-and-examples)
  - [nicedouble/StreamlitAntdComponents: A Streamlit component to display Antd-Design](https://github.com/nicedouble/StreamlitAntdComponents)
    - [Documentation](https://nicedouble-streamlitantdcomponentsdemo-app-middmy.streamlit.app/)
    - [nicedouble/StreamlitAntdComponentsDemo: Streamlit-antd-components demo app](https://github.com/nicedouble/StreamlitAntdComponentsDemo/)

---

No longer needed. We will set this in this repository

Edit Streamlit config `~/.streamlit/config.toml`

> Set enableStaticServing = true under [server] in your config file, or environment variable `STREAMLIT_SERVER_ENABLE_STATIC_SERVING=true`.

```
streamlit config show
```

```toml
[server]
enableStaticServing = true
```
