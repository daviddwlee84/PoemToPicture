from typing import Optional
import pandas as pd
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Poem:
    id: Optional[int] = None
    title: Optional[str] = None
    author: Optional[str] = None
    dynasty: Optional[str] = None
    content: Optional[str] = None


class PoemManager:
    """
    https://stackoverflow.com/questions/4019971/how-to-implement-iter-self-for-a-container-object-python
    """

    _data: pd.DataFrame

    def __init__(self, tsv_file: str = None) -> None:
        if tsv_file:
            self._data = self.load(tsv_file)

    def load(self, tsv_file: str) -> pd.DataFrame:
        """
        TODO: able to incrementally load multiple TSV files
        """
        return pd.read_csv(tsv_file, sep="\t", index_col=None)

    def __getitem__(self, index: int) -> Poem:
        return Poem.from_dict(self._data.iloc[index].to_dict())

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self) -> Poem:
        for idx, poem in self._data.iterrows():
            yield Poem.from_dict(poem.to_dict())
    
    def get_by_id(self, index: int) -> Poem:
        return Poem.from_dict(self._data.loc[index].to_dict())


if __name__ == "__main__":
    import os

    curr_dir = os.path.dirname(os.path.abspath(__file__))
    manager = PoemManager(os.path.join(curr_dir, "data/poems.tsv"))
    # for poem in manager:
    #     print(poem)
    # print(manager[3])

    data = []
    names = []
    prompt_version = "naive_dalle2"
    for poem in manager:
        for version in ["v1", "v2"]:
            if version == "v1" and poem.id > 10:
                continue
            if version == "v2" and poem.id > 41:
                continue
            name = f"{poem.id}_{poem.title}_{prompt_version}_{version}.png"
            assert os.path.exists(
                os.path.join(
                    curr_dir,
                    "static/images",
                )
            )
            data.append(
                {
                    "poem_id": poem.id,
                    "poem_name": poem.title,
                    "prompt_name": prompt_version,
                    "version": version,
                    "vote": 0,
                }
            )
            names.append(name)
    print(names)
    print(df := pd.DataFrame(data).rename_axis("id"))
    df.to_csv("votes.tsv", sep="\t")
