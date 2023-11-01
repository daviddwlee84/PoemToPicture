from typing import List, Optional, Literal
import os
from glob import glob
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from poem import Poem


@dataclass_json
@dataclass
class Prompt:
    name: str
    dalle: str
    system: Optional[str] = None
    chatgpt: Optional[str] = None

    def format(
        self,
        prompt: Literal["dalle", "system", "chatgpt"],
        poem: Poem = None,
        last_layer_output: str = None,
    ) -> Optional[str]:
        string: str = getattr(self, prompt)
        if not string:
            return string
        string = string.format(**poem.to_dict(), output=last_layer_output)
        return string


class PromptManager:
    """
    TODO: support chain of thought
    """

    _data: List[Prompt]

    def __init__(self, json_dir: str) -> None:
        self._data = []
        self.json_dir = json_dir
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

    def get_by_name(self, name: str) -> Optional[Prompt]:
        for prompt in self._data:
            if prompt.name == name:
                return prompt
        return None

    def append(self, prompt: Prompt, save: bool = True) -> None:
        self._data.append(prompt)
        if save:
            with open(
                os.path.join(self.json_dir, f"{prompt.name}.json"),
                "w",
                encoding="utf-8",
            ) as fp:
                fp.write(prompt.to_json(indent=4, ensure_ascii=False))


if __name__ == "__main__":
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    poem = Poem(id=None, title="登鸛雀樓", author="王之渙", content="白日依山盡，黃河入海流。欲窮千里目，更上一層樓。")
    manager = PromptManager(os.path.join(curr_dir, "data/prompts"))
    for prompt in manager:
        print(prompt)
        print(prompt.format("dalle", poem))
        print(
            prompt.format(
                "dalle",
                poem,
                last_layer_output="太陽挨著西山慢慢下沉，黃河向著大海波濤滾滾。想看到遠處更美的景色，必須繼續登樓再上一層。",
            )
        )
