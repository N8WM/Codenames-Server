import websockets, asyncio, sys
from player_config import get_codemaster, get_guesser
from online_game import Game


# Game configuration
WORDPOOL_FILE = "game_wordpool.txt"
CODEMASTER = "human"
GUESSER = "human"


async def RunGame(clientsocket):
    global WORDPOOL_FILE, CODEMASTER, GUESSER, CM_CLASS, G_CLASS, cm_kwargs, g_kwargs
    if CODEMASTER == "human":
        cm_kwargs = {"clientsocket": clientsocket}
    if GUESSER == "human":
        g_kwargs = {"clientsocket": clientsocket}

    print("Starting game... (team red)")

    Game.clear_results()
    seed = "time"

    await Game(
        CM_CLASS, G_CLASS, clientsocket, seed,
        do_print=False,
        game_name="Online Game",
        cm_kwargs=cm_kwargs,
        g_kwargs=g_kwargs,
        wordpool_file=WORDPOOL_FILE
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
    print("Loading bots...", end=" ", flush=True)
    CM_CLASS, cm_kwargs = get_codemaster(CODEMASTER).load()
    G_CLASS, g_kwargs = get_guesser(GUESSER).load()
    print("Bots loaded.")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[Server Closed]\nCleaning up...")
        sys.exit()
