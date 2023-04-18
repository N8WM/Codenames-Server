import websockets, asyncio, sys
from online_game import Game
from players.online import OnlineHumanCodemaster, OnlineHumanGuesser
from players.vector_codemaster import VectorCodemaster
from players.vector_guesser import VectorGuesser

# enum for the roles
class Role(enumerate):
    """Enum for the roles"""
    CODEMASTER = 0
    GUESSER = 1
    NONE = 2

# set the role of the human player
HUMAN_ROLE = Role.GUESSER

glove_50d = None
glove_100d = None
w2v = None

def load_resources():
    """Load the resources"""
    global glove_50d, glove_100d, w2v
    if glove_50d is None:
        glove_50d = Game.load_glove_vecs("players/glove.6B.50d.txt")
    if glove_100d is None:
        glove_100d = Game.load_glove_vecs("players/glove.6B.100d.txt")
    if w2v is None:
        w2v = Game.load_w2v("players/GoogleNews-vectors-negative300.bin")

async def RunGame(clientsocket):
    """An example of a game with a human codemaster and a bot guesser"""

    print("Loading resources...", end=" ", flush=True)
    load_resources()
    print("Loaded.")
    print("Starting game... (team red)")

    Game.clear_results()
    seed = "time"

    bot_cm_class    = VectorCodemaster
    bot_g_class     = VectorGuesser
    human_cm_class  = OnlineHumanCodemaster
    human_g_class   = OnlineHumanGuesser
    bot_cm_kwargs   = {"vectors": [w2v, glove_100d], "distance_threshold": 0.7, "same_clue_patience": 1, "max_red_words_per_clue": 3}
    bot_g_kwargs    = {"vectors": [w2v, glove_100d]}
    human_cm_kwargs = {"clientsocket": clientsocket}
    human_g_kwargs  = {"clientsocket": clientsocket}

    cm_class  = human_cm_class  if HUMAN_ROLE is Role.CODEMASTER else bot_cm_class
    g_class   = human_g_class   if HUMAN_ROLE is Role.GUESSER    else bot_g_class
    cm_kwargs = human_cm_kwargs if HUMAN_ROLE is Role.CODEMASTER else bot_cm_kwargs
    g_kwargs  = human_g_kwargs  if HUMAN_ROLE is Role.GUESSER    else bot_g_kwargs

    await Game(
        cm_class, g_class, clientsocket, seed,
        do_print=False,
        game_name="Online Game",
        cm_kwargs=cm_kwargs,
        g_kwargs=g_kwargs
    ).run()

async def handler(websocket):
    print(await websocket.recv())
    await RunGame(websocket)

async def main():
    print("Starting server...", end=" ", flush=True)
    async with websockets.serve(handler, "localhost", 8001):
        print("Server started.\nWaiting for connection...", end=" ")
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[Server Closed]\nCleaning up...")
        sys.exit()
