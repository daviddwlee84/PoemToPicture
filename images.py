from typing import Literal, Union, List
import pandas as pd
import re
import os
from poem import Poem
from prompts import Prompt


class ImageVoteManager:
    _data: pd.DataFrame

    def __init__(self, vote_path: str, image_dir: str, verbose: bool = False):
        self.vote_path = vote_path
        self.image_dir = image_dir
        self.verbose = verbose

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


class UserVoteManager(ImageVoteManager):
    _user_votes: pd.DataFrame

    def __init__(
        self,
        vote_path: str,
        user_votes_path: str,
        image_dir: str,
        verbose: bool = False,
    ):
        super().__init__(vote_path, image_dir, verbose)
        self.user_votes_path = user_votes_path
        user_votes_df = pd.read_csv(user_votes_path, sep="\t", index_col=0)
        self._user_votes = user_votes_df
        if initialized_count := self.initial_new_image() > 0:
            if self.verbose:
                print(f"Add additional {initialized_count} images.")
            self.save_votes()

    def initial_new_image(self) -> int:
        """
        https://stackoverflow.com/questions/58434018/pandas-adding-row-with-all-values-zero
        """
        initial_rows = 0
        for index in self._data.index.difference(self._user_votes.index):
            self._user_votes.loc[index] = 0
            initial_rows += 1
        return initial_rows

    def initial_new_user(self, user: str) -> bool:
        if user not in self.get_existing_users():
            self._user_votes[user] = 0
            return True
        return False

    def get_existing_users(self) -> List[str]:
        return self._user_votes.columns.to_list()

    def get_joined_data(self) -> pd.DataFrame:
        return self._data.drop("vote", axis=1).join(
            self._user_votes, lsuffix=None, rsuffix="_votes"
        )

    def save_votes(self, user_votes_path: str = None) -> None:
        if user_votes_path is None:
            user_votes_path = self.user_votes_path
        self._user_votes.to_csv(user_votes_path, sep="\t")

    def get_streamlit_data(self) -> pd.DataFrame:
        """
        TODO: join poem content and sort with poem_id & prompt_name & version
        """

    def update_user_votes(self, streamlit_df: pd.DataFrame, save: bool = True):
        """
        Save votes to file and update self._user_votes
        https://stackoverflow.com/questions/37400246/pandas-update-multiple-columns-at-once
        """
        user_votes = streamlit_df[self.get_existing_users()].reindex_like(
            self._user_votes
        )
        self._user_votes.loc[:, self.get_existing_users()] = user_votes
        if save:
            self.save_votes()
            # user_votes.sort_index().to_csv(self.user_votes_path, sep='\t')


def _test_vote_manager():
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


def _test_user_vote():
    curr_dir = os.path.dirname(os.path.abspath(__file__))

    manager = UserVoteManager(
        os.path.join(curr_dir, "data/votes.tsv"),
        os.path.join(curr_dir, "data/user_votes.tsv"),
        os.path.join(curr_dir, "static/images"),
        verbose=True,
    )

    print(manager._user_votes)
    print(manager.get_existing_users())
    print(manager.get_joined_data())
    import ipdb

    ipdb.set_trace()


if __name__ == "__main__":
    # _test_vote_manager()
    _test_user_vote()
