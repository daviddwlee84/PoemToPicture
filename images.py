from typing import Literal, Union
import pandas as pd
import re
import os
from poem import Poem
from prompts import Prompt


class ImageVoteManager:
    _data: pd.DataFrame

    def __init__(self, vote_path: str, image_dir: str):
        self.vote_path = vote_path
        self.image_dir = image_dir

        vote_data = pd.read_csv(
            vote_path,
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

        # TODO: use more elegant way
        if not image_dir.endswith("/"):
            image_dir += "/"

        vote_data["image_file"] = (
            image_dir
            + vote_data["poem_id"]
            + "_"
            + vote_data["poem_name"]
            + "_"
            + vote_data["prompt_name"]
            + "_"
            + vote_data["version"]
            + ".png"
        )

        for file_path in vote_data["image_file"]:
            assert os.path.exists(file_path)

        vote_data["streamlit_image_file"] = (
            "/app/static/images/"
            + vote_data["poem_id"]
            + "_"
            + vote_data["poem_name"]
            + "_"
            + vote_data["prompt_name"]
            + "_"
            + vote_data["version"]
            + ".png"
        )

        self._data = vote_data

    def save(self, vote_path: str = None) -> None:
        if vote_path is None:
            vote_path = self.vote_path
        self._data[["poem_id", "poem_name", "prompt_name", "version", "vote"]].to_csv(
            vote_path, sep="\t"
        )
    
    # def get_all_poems_indices(self) -> pd.Series:
    #     return self._data['poem_id'].unique()

    def get_images_by_id(self, index: Union[int, str]) -> pd.DataFrame:
        return self._data[self._data["poem_id"] == str(index)]

    def get_images_by_title(self, title: str) -> pd.DataFrame:
        return self._data[self._data["poem_name"] == title]

    def get_images_by_prompt(self, prompt_name: str) -> pd.DataFrame:
        return self._data[self._data["prompt_name"] == prompt_name]

    def get_images_by_vote(self, vote: Literal[0, 1, 2, 3, 4, 5]) -> pd.DataFrame:
        return self._data[self._data["vote"] == vote]

    def get_images_by_poem_prompt(self, poem: Poem, prompt: Prompt) -> pd.DataFrame:
        return self._data[
            (self._data["poem_id"] == str(poem.id))
            & (self._data["poem_name"] == poem.title)
            & (self._data["prompt_name"] == prompt.name)
        ]

    @staticmethod
    def get_latest_version(filtered_data: pd.DataFrame) -> str:
        """
        TODO: Also support series and list
        """
        if filtered_data.empty:
            return "v0"
        return filtered_data["version"].sort_values(ascending=False).iloc[0]

    @staticmethod
    def get_next_version(version: str) -> str:
        version_int = int(re.search(r"v(\d+)", version).group(1))
        return f"v{version_int + 1}"

    def get_new_file_path(
        self, poem: Poem, prompt: Prompt, update_data: bool = True
    ) -> str:
        images = self.get_images_by_poem_prompt(poem, prompt)
        version = self.get_next_version(self.get_latest_version(images))
        file_path = os.path.join(
            self.image_dir, f"{poem.id}_{poem.title}_{prompt.name}_{version}.png"
        )
        if update_data:
            self._data.loc[len(self._data)] = {
                "poem_id": str(poem.id),
                "poem_name": poem.title,
                "prompt_name": prompt.name,
                "version": version,
                "vote": 0,
                "image_file": file_path,
            }
            # self.save()

        return file_path


if __name__ == "__main__":
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    manager = ImageVoteManager(
        os.path.join(curr_dir, "data/votes.tsv"),
        os.path.join(curr_dir, "static/images"),
    )

    images = manager.get_images_by_id(2)
    print(latest_version := manager.get_latest_version(images))
    print(next_version := manager.get_next_version(latest_version))

    from poem import PoemManager
    from prompts import PromptManager

    poems = PoemManager(os.path.join(curr_dir, "data/poems.tsv"))
    prompts = PromptManager(os.path.join(curr_dir, "data/prompts"))
    poem = poems.get_by_id(100)
    prompt = prompts.get_by_name("naive_dalle2")
    print(new_file_path := manager.get_new_file_path(poem, prompt, update_data=True))
    print(new_file_path := manager.get_new_file_path(poem, prompt, update_data=True))
    print(new_file_path := manager.get_new_file_path(poem, prompt, update_data=True))
    poem = poems.get_by_id(10)
    print(new_file_path := manager.get_new_file_path(poem, prompt, update_data=True))
