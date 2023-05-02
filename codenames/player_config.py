import sys, importlib
from typing import List, Literal, Tuple, Union, Callable
from online_game import Game
from players.codemaster import Codemaster
from players.guesser import Guesser


class player_config:
    """
    # A configuration for a player, including the role, name, and class to load
    - Surround kwargs with a lambda if they need to be generated at runtime and/or
    any of them require expensive computation
    """
    def __init__(self,
        role: Literal["codemaster", "guesser"], name: str,
        root: Union[str, None], module: str, classname: str,
        kwargs: Union[dict, Callable[[], dict]] = {}
    ):
        """
        # Parameters
        - `role`: The role of the player, either `"codemaster"` or `"guesser"`
        - `name`: The name of the player, used to identify it in the game
        - `root`: The root directory of the module to load, or `None` if it is
           already in the path
        - `module`: The module to load the class from
        - `classname`: The name of the class to load

        # Optional Parameters
        - `kwargs`: The keyword arguments to pass to the class's constructor
           (default `{}`)
        """
        self.role = role
        self.name = name
        self.root = root
        self.module = module
        self.classname = classname
        self.kwargs = kwargs
    
    def load(self) -> Tuple[Union[Codemaster, Guesser], dict]:
        if self.root is not None:
            sys.path.append(self.root)
        module = importlib.import_module(self.module)
        class_ = getattr(module, self.classname)
        kwargs = self.kwargs if isinstance(self.kwargs, dict) else self.kwargs()
        return class_, kwargs


# Place your player configurations here
PLAYERS = [

    # Human codemaster
    player_config(
        role="codemaster",
        name="human",
        root=None,
        module="players.online",
        classname="OnlineHumanCodemaster",
        kwargs={}
    ),

    # Example vector codemaster
    player_config(
        role="codemaster",
        name="vector",
        root=None,
        module="players.vector_codemaster",
        classname="VectorCodemaster",
        kwargs=lambda: {
            "vectors": [
                Game.load_w2v("players/GoogleNews-vectors-negative300.bin"),
                Game.load_glove_vecs("players/glove.6B.100d.txt")
            ],
            "distance_threshold": 0.7,
            "same_clue_patience": 1,
            "max_red_words_per_clue": 3
        }
    ),

    # Example ada embedding codemaster
    player_config(
        role="codemaster",
        name="ada",
        root=None,
        module="players.ada_codemaster",
        classname="ADACodemaster",
        kwargs={
            "distance_threshold": 0.7,
            "same_clue_patience": 1,
            "max_words_per_clue": 3
        }
    ),

    # Human guesser
    player_config(
        role="guesser",
        name="human",
        root=None,
        module="players.online",
        classname="OnlineHumanGuesser",
        kwargs={}
    ),

    # Example vector guesser
    player_config(
        role="guesser",
        name="vector",
        root=None,
        module="players.vector_guesser",
        classname="VectorGuesser",
        kwargs=lambda: {
            "vectors": [
                Game.load_w2v("players/GoogleNews-vectors-negative300.bin"),
                Game.load_glove_vecs("players/glove.6B.100d.txt")
            ]
        }
    ),

    # Example ada embedding guesser
    player_config(
        role="guesser",
        name="ada",
        root=None,
        module="players.ada_guesser",
        classname="ADAGuesser",
        kwargs={}
    )
]

# utility functions for getting players
def get_codemasters() -> List[player_config]:
    return [p for p in PLAYERS if p.role == "codemaster"]

def get_guessers() -> List[player_config]:
    return [p for p in PLAYERS if p.role == "guesser"]

def get_codemaster(name: str) -> player_config:
    return next(p for p in PLAYERS if p.role == "codemaster" and p.name == name)

def get_guesser(name: str) -> player_config:
    return next(p for p in PLAYERS if p.role == "guesser" and p.name == name)
