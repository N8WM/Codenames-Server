import websockets, asyncio, sys
from online_game import Game
from players.online import OnlineHumanCodemaster, OnlineHumanGuesser
from players.vector_codemaster import VectorCodemaster
from players.vector_guesser import VectorGuesser

glove_50d = None
glove_100d = None
w2v = None

async def RunGame(clientsocket):
    """An example of a game with a human codemaster and a bot guesser"""

    print("Loading resources...", end=" ", flush=True)
    global glove_50d, glove_100d, w2v
    if glove_50d is None:
        glove_50d = Game.load_glove_vecs("players/glove.6B.50d.txt")
    if glove_100d is None:
        glove_100d = Game.load_glove_vecs("players/glove.6B.100d.txt")
    if w2v is None:
        w2v = Game.load_w2v("players/GoogleNews-vectors-negative300.bin")
    print("Loaded.")
    print("Starting game... (team red)")

    Game.clear_results()
    seed = 0

    g_kwargs = {"vectors": [w2v, glove_100d]}

    await Game(
        OnlineHumanCodemaster,
        VectorGuesser,
        clientsocket,
        seed=seed,
        do_print=True,
        game_name="human",
        cm_kwargs={
            "clientsocket": clientsocket
        },
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
        print("\n\n[Server Closed]")
        sys.exit()
