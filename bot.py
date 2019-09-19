import logging
import os
import time
from slack import WebClient, RTMClient

from slackeventsapi import SlackEventAdapter
from tetris import Tetris, HEIGHT, WIDTH
from tetris_thread import TetrisThread

import nest_asyncio
nest_asyncio.apply()


# get slack client
token = os.getenv("SLACK_API_TOKEN")
sc = WebClient(token=token)
rtmclient = RTMClient(token=token)

# load bot info
BOT_NAME = os.getenv("BOT_NAME")
bot_id = ""
resp = sc.api_call("users.list")
if resp.get('ok'):
    for user in resp.get('members'):
        if 'name' in user and user.get('name') == BOT_NAME:
            bot_id = user.get('id')
BOT_ID = bot_id

# make logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# log to file
fh = logging.FileHandler("bot.log")
logger.addHandler(fh)

# log to stdout
sh = logging.StreamHandler()
logger.addHandler(sh)

# set logging format
formatter = logging.Formatter(
    "%(asctime)s : %(name)s : %(lineno)d : %(levelname)s : %(message)s")
fh.setFormatter(formatter)
sh.setFormatter(formatter)

# define omits
omits = {
    "d": "down",
    "h": "harddrop",
    "l": "left",
    "r": "right",
    "t": "turn",
}

# define support messages
texts = {
    "start": "game start!",
    "down": "down",
    "harddrop": "harddrop",
    "left": "left",
    "right": "right",
    "turn": "turn",
    "stop": "stop",
    "help": (
        "usage\n"
        "```start: start new game\n"
        "down|d: move a block down\n"
        "harddrop|h: move a block to harddrop\n"
        "left|l [n] (1~9, default 1): move a block to left [n] times\n"
        "right|r [n] (1~9, default 1): move a block to right [n] times\n"
        "turn|t: turn a block\n"
        "stop: stop the game```"
    ),
    "playing": "already playing!",
    "not_playing": "go ahead with start command!",
    "cannot_move": "cannot move a block!",
    "over": "game over!",
}


def make_message(command):
    return texts.get(command, "message not defined")


def parse_commands(commands):
    parsed = []
    rep = 1
    for c in reversed(commands):
        try:
            rep = int(c)
            continue
        except:
            if c in omits.keys():
                c = omits.get(c)
            parsed.extend([c] * rep)
            rep = 1
    return parsed[::-1]


# get tetris thread
tetris_threads = {}


@RTMClient.run_on(event='message')
def handle_message(**event_data):
    message = event_data.get("data")
    mentions = [BOT_NAME, "<@%s>" % BOT_ID]
    if message.get("text") and message["text"].split()[0] in mentions:
        ts = message.get("thread_ts") or message["ts"]

        tetris_thread = tetris_threads.get(ts, None)
        if tetris_thread == None:
            tetris_thread = TetrisThread(sc, ts, message["channel"])
            tetris_threads[ts] = tetris_thread

        commands = parse_commands(message["text"].split()[1:])
        message_text = ""
        for i, command in enumerate(commands):
            if not tetris_thread.tetris.player:
                tetris_thread.tetris.player = ts

            try:
                if command == "start":
                    if tetris_thread.tetris.playing:
                        message_text = make_message("playing")
                    else:
                        tetris_thread.eval_command(command)
                        message_text = make_message(command)
                        message_text += "\n"
                        message_text += tetris_thread.get_playground()
                else:
                    if tetris_thread.tetris.playing:
                        if tetris_thread.eval_command(command):
                            message_text = make_message(command)
                            message_text += "\n"
                            message_text += tetris_thread.get_playground()
                        else:
                            message_text = make_message("cannot_move")
                            message_text += "\n"
                            message_text += tetris_thread.get_playground()
                    else:
                        message_text = make_message("not_playing")
            except Exception as e:
                logger.warn(e)
                message_text = make_message("help")

            if i + 1 == len(commands) or command != commands[i + 1]:
                tetris_thread.post_message(message_text)


if __name__ == "__main__":
    # start rtm client
    rtmclient.start()
