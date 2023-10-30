from typing import List, Optional, Literal
import os
from glob import glob
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Prompt:
    name: str
    dalle: str
    system: Optional[str] = None
    chatgpt: Optional[str] = None


class PromptManager:
    """
    TODO: support chain of thought
    """

    _data: List[Prompt] = []

    def __init__(self, json_dir: str) -> None:
        for path in glob(os.path.join(json_dir, "*.json")):
            with open(path, "r", encoding="utf-8") as fp:
                self._data.append(Prompt.from_json(fp.read()))

    def __getitem__(self, index: int):
        return self._data[index]

    def __len__(self):
        return len(self._data)

    def __iter__(self):
        for prompt in self._data:
            yield prompt


if __name__ == "__main__":
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    manager = PromptManager(os.path.join(curr_dir, "data/prompts"))
    for prompt in manager:
        print(prompt)
