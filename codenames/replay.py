from abc import ABC, abstractmethod
import json
import os
from typing import Literal
from players.codemaster import Codemaster
from players.guesser import Guesser


class Action(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def to_json(self) -> str:
        pass

    @abstractmethod
    def get_role(self) -> Literal[
        "blue_codemaster", "blue_guesser", "red_codemaster", "red_guesser"
    ]:
        pass


class GuessAction(Action):
    def __init__(self, word: str, color: Literal["red", "blue"]):
        self.word = word
        self.role = f"{color}_guesser"

    def to_json(self) -> str:
        return json.dumps({
            "word": self.word
        })

    def get_role(self) -> Literal[
        "blue_guesser", "red_guesser"
    ]:
        return self.role


class HintAction(Action):
    def __init__(self, hint: str, num: int, color: Literal["red", "blue"]):
        self.hint = hint
        self.num = num
        self.role = f"{color}_codemaster"

    def to_json(self) -> str:
        return json.dumps({
            "hint": self.hint,
            "num": self.num
        })

    def get_role(self) -> Literal[
        "blue_codemaster", "red_codemaster"
    ]:
        return self.role


class Replay():
    def __init__(self, seed):
        self.seed = seed
        self.actions = {
            "blue_codemaster": [],
            "blue_guesser": [],
            "red_codemaster": [],
            "red_guesser": []
        }

    def add_action(
        self,
        action: Action,
    ):
        self.actions[action.data["role"]].append(action.to_json())

    def to_json(self):
        return json.dumps({
            "seed": self.seed,
            "actions": self.actions
        })


class ReplayHandler(Codemaster, Guesser):
    def __init__(self, seed, replay_id: str, replay_folder: str = "replays", is_recording=False):
        self.seed = seed
        self.replay_id = replay_id
        self.replay_folder = replay_folder
        self.is_recording = is_recording
        self.replay = None
        self.is_broken = False

        if is_recording:
            self.setup_replay()
        else:
            self.get_replay()

    def get_replay_path(self):
        return f"{self.replay_folder}/{self.replay_id}.json"
    
    def get_replay(self):
        try:
            with open(self.get_replay_path(), "r") as f:
                self.replay = json.load(f)
        except Exception as e:
            print(e)
            print("Could not load replay.")
            self.is_broken = True
    
    def setup_replay(self):
        try:
            if not os.path.exists(self.replay_folder):
                os.mkdir(self.replay_folder)
        except Exception as e:
            print(e)
            print("Could not create or access replay folder. Replays will not be saved.")
            self.is_broken = True
            return
        
        try:
            with open(self.get_replay_path(), "w") as f:
                f.write()
        except Exception as e:
            print(e)
            print("Could not save replay.")
            self.is_broken = True
            return
        
        self.replay = Replay(self.seed)
