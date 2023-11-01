from typing import Tuple, Dict, Optional
import requests
import openai
from images import ImageVoteManager
from poem import Poem
from prompts import Prompt
import os


class InferenceBase:
    _api_config: Dict[str, str]
    _deployment_name: Optional[str] = None

    @staticmethod
    def save_image(image_url: str, image_path: str) -> None:
        # download the image
        generated_image = requests.get(image_url).content
        with open(image_path, "wb") as image_file:
            image_file.write(generated_image)

    def dalle2(self, prompt: str, size: str = "1024x1024", n: int = 1) -> str:
        """
        Return image URL

        https://platform.openai.com/docs/guides/images/image-generation
        """
        if self._deployment_name is not None:
            generation_response = openai.Image.create(
                prompt=prompt,
                size=size,
                n=n,
                deployment_id=self._deployment_name,
                **self._api_config
            )
        else:
            generation_response = openai.Image.create(
                prompt=prompt, size=size, n=n, **self._api_config
            )
        # extract image URL from response
        image_url = generation_response["data"][0]["url"]
        return image_url

    def chatgpt(
        self,
        prompt: str,
        system_prompt: str = "You are a helpful assistant with professional knowledge about painting and Chinese poems.",
        temperature: float = 0.5,
        max_response_tokens: int = 1024,
        model_name: str = "gpt-3.5-turbo",
    ) -> str:
        conversation = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": prompt},
        ]
        # Send a completion call to generate a response
        # https://platform.openai.com/docs/api-reference/chat/create
        # openai.error.InvalidRequestError: Must provide an 'engine' or 'model' parameter to create a <class 'openai.api_resources.chat_completion.ChatCompletion'>
        if self._deployment_name is not None:
            response = openai.ChatCompletion.create(
                # engine=self._deployment_name,
                # model='gpt-35-turbo-16k',
                deployment_id=self._deployment_name,
                messages=conversation,
                temperature=temperature,
                max_tokens=max_response_tokens,
                **self._api_config
            )
        else:
            response = openai.ChatCompletion.create(
                model=model_name,
                messages=conversation,
                temperature=temperature,
                max_tokens=max_response_tokens,
                **self._api_config
            )
        # TODO: the post processing seems to be used for English...
        response_text = (
            response["choices"][0]["message"]["content"]
            .replace("\n", " ")
            .replace(" .", ".")
            .strip()
        )
        return response_text


class AzureInference(InferenceBase):
    def __init__(
        self,
        deployment_name: str,
        api_base: str,
        api_key: str,
        api_version: str = "2023-06-01-preview",
    ) -> None:
        self._deployment_name = deployment_name
        self._api_config = {
            "api_base": api_base,
            "api_key": api_key,
            "api_version": api_version,
            "api_type": "azure",
        }


class OpenAIInference(InferenceBase):
    def __init__(
        self,
        api_key: str,
    ) -> None:
        self._deployment_name = None
        self._api_config = {
            "api_key": api_key,
        }


class Pipeline:
    """
    TODO: callbacks to dump intermediate result
    """

    image_vote_manager: ImageVoteManager
    api: InferenceBase

    def __init__(
        self, image_vote_manager: ImageVoteManager, api: InferenceBase
    ) -> None:
        self.image_vote_manager = image_vote_manager
        self.api = api

    def __call__(
        self, prompt: Prompt, poem: Poem, temperature: float = 0.5
    ) -> Tuple[str, str]:
        image_path = self.image_vote_manager.get_new_file_path(
            poem, prompt, update_data=True
        )
        if prompt.system and prompt.chatgpt:
            output = self.api.chatgpt(
                prompt.format("chatgpt", poem),
                prompt.format("system", poem),
                temperature=temperature,
            )
            image_url = self.api.dalle2(prompt.format("dalle", poem, output))
        else:
            image_url = self.api.dalle2(prompt.format("dalle", poem))
        self.api.save_image(image_url, image_path)
        if os.path.exists(image_path):
            # Only if image successfully saved then update the vote data
            self.image_vote_manager.save()
        return (image_url, image_path)


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()

    # deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
    # api_base = os.getenv("AZURE_OPENAI_ENDPOINT")
    # api_key = os.getenv("AZURE_OPENAI_KEY")
    # api = AzureInference(deployment_name, api_base, api_key)

    api_key = os.getenv("OPENAI_API_KEY")
    api = OpenAIInference(api_key)

    # image_url = api.dalle2(
    #     "Realistic painting of a dystopian industrial city with towering factories, pollution-filled air, and a gloomy sky."
    # )
    # print(image_url)
    # api.save_image(image_url, "DystopianIndustrialCityscape.png")

    response = api.chatgpt(
        "3 times 4 equals?",
        "You are a math expert that can solve complex math problem.",
    )
    print(response)
