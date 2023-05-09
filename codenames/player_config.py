import sys, importlib
from typing import List, Literal, Tuple, Union, Callable
from online_game import Game
from players.codemaster import Codemaster
from players.guesser import Guesser

resources = {}


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
           already in the path (or the module is in the current directory)
        - `module`: The module to load the codemaster/guesser class from
        - `classname`: The name of the codemaster/guesser class to load from
           the module

        # Optional Parameters
        - `kwargs`: The keyword arguments to pass to the class's constructor
           (default `{}`). If this is a callable, it will be called to generate
              the kwargs at runtime.
            - Callable kwargs are useful if they require expensive computation or
              need to be loaded into memory at runtime.
            - In this case, it is recommended to use a lambda that returns the
              kwargs to avoid loading the kwargs when a player config is not used.
            - If you intend to use the same resource in multiple players, it is
              recommended to use the `resource` class and pass it to the kwargs
              with `resource("name", func, *args, **kwargs).get()`. This will
              ensure that resources of the same name are only loaded once and
              can be shared between players.

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


class resource:
    """
    # A resource that can be shared between players
    - If the resource has already been loaded, it will be reused
    - If the resource has not been loaded, it will remain unloaded until it is
        needed, at which point it will be loaded and cached
    - This is useful for expensive resources that are shared between players
    """
    def __init__(self, name: str, func: Callable, *args, **kwargs):
        """
        # Parameters
        - `name`: The name of the resource, used to identify when it has already
            been loaded
        - `func`: The function to call to load the resource
        - `*args`: The positional arguments to pass to `func`
        - `**kwargs`: The keyword arguments to pass to `func` - not to be confused
            with the arguments to pass to player_config's `kwargs` parameter.
        """
        global resources
        if name in resources:
            self.ref = resources[name]
        else:
            self.ref = None
            self.name = name
            self.func = func
            self.args = args
            self.kwargs = kwargs
            self.value = None
            resources[name] = self

    def get(self):
        """
        # Returns
        - The resource, loaded if necessary
        """
        if self.ref is not None:
            return self.ref.get()
        if self.value is None:
            self.value = self.func(*self.args, **self.kwargs)
        return self.value


####################################################################
############## Place your player configurations below ##############
####################################################################

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
                resource("w2v", Game.load_w2v, "players/GoogleNews-vectors-negative300.bin").get(),
                resource("glove", Game.load_glove_vecs, "players/glove.6B.100d.txt").get()
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
                resource("w2v", Game.load_w2v, "players/GoogleNews-vectors-negative300.bin").get(),
                resource("glove", Game.load_glove_vecs, "players/glove.6B.100d.txt").get()
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
