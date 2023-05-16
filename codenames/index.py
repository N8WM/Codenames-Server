import websockets, asyncio, sys
from replay import ReplayHandler
from player_config import get_codemaster, get_guesser
from online_game import Game


# Game configuration
WORDPOOL_FILE = "game_wordpool.txt"
CODEMASTER = "vector"
GUESSER = "human"
CM_CLASS, G_CLASS, cm_kwargs, g_kwargs = None, None, {}, {}

# Replay configuration
DO_REPLAY = False
REPLAY_ID = None # "1684222943.9041533"


async def RunReplay(clientsocket):
    global REPLAY_ID
    print(f"Replaying game {REPLAY_ID}... (team red)", flush=True)
    await Game(
        ReplayHandler, ReplayHandler, clientsocket,
        do_print=True,
        game_name="Online Game",
        cm_kwargs={"replay_id": REPLAY_ID},
        wordpool_file=WORDPOOL_FILE,
        is_replaying=True
    ).run()


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
        do_print=True,
        game_name="Online Game",
        cm_kwargs=cm_kwargs,
        g_kwargs=g_kwargs,
        do_record=True,
        wordpool_file=WORDPOOL_FILE
    ).run()

async def handler(websocket):
    global DO_REPLAY
    print(await websocket.recv())
    if DO_REPLAY:
        await RunReplay(websocket)
    else:
        await RunGame(websocket)

async def main():
    print("Starting server...", end=" ", flush=True)
    async with websockets.serve(handler, "localhost", 8001):
        print("Server started.\nWaiting for connection...", end=" ")
        await asyncio.Future()

if __name__ == "__main__":
    if not DO_REPLAY:
        print("Loading bots...", end=" ", flush=True)
        CM_CLASS, cm_kwargs = get_codemaster(CODEMASTER).load()
        G_CLASS, g_kwargs = get_guesser(GUESSER).load()
        print("Bots loaded.")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[Server Closed]\nCleaning up...")
        sys.exit()
