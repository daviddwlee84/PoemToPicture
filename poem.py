import pandas as pd
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Poem:
    id: int
    title: str
    author: str
    dynasty: str
    content: str


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

    def __getitem__(self, index: int):
        return Poem.from_dict(self._data.iloc[index].to_dict())

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        for idx, poem in self._data.iterrows():
            yield Poem.from_dict(poem.to_dict())


if __name__ == "__main__":
    import os

    curr_dir = os.path.dirname(os.path.abspath(__file__))
    manager = PoemManager(os.path.join(curr_dir, "data/poems.tsv"))
    for poem in manager:
        print(poem)
    print(manager[3])
