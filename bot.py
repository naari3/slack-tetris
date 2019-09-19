import logging
import os
import time
from slack import WebClient, RTMClient

from slackeventsapi import SlackEventAdapter
from tetris import Tetris, HEIGHT, WIDTH

import nest_asyncio
nest_asyncio.apply()


# get slack client
token = os.getenv("SLACK_API_TOKEN")
sc = WebClient(token=token)
rtmclient = RTMClient(token=token)

# get tetris
tetris = Tetris()

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

# define block emojis
emojis = {
    -1: ":tenjiblock_dot:",
    0: ":mu:",
    1: ":tetris_z:",
    2: ":tetris_l:",
    3: ":tetris_s:",
    4: ":tetris_j:",
    5: ":tetris_o:",
    6: ":tetris_i:",
    7: ":tetris_t:",
}


def start():
    tetris.playing = True
    tetris.clear()


def down():
    success = tetris.down()
    if not success:
        tetris.player = None
        tetris.playing = False
    return success


def harddrop():
    success = tetris.harddrop()
    if not success:
        tetris.player = None
        tetris.playing = False
    return success


def left():
    return tetris.move(-1)


def right():
    return tetris.move(1)


def turn():
    return tetris.turn()


def stop():
    tetris.player = None
    tetris.playing = False
    return True


def get_playground():
    playground = ""
    for y in range(HEIGHT - 1):
        for x in range(WIDTH - 2):
            # left lane
            if x == 0:
                playground += emojis[-1]

            # background or block
            b = tetris.block(x + 1, y)
            if b >= 1:
                playground += emojis[b]
            else:
                playground += emojis[0]

            # right lane
            if x == 9:
                playground += emojis[-1]
                playground += "\n"
    return playground


def post_message(channel, text):
    # with_playground = ["start", "down", "harddrop", "left", "right", "turn"]
    sc.chat_postMessage(
        channel=channel,
        text=text,
        thread_ts=tetris.player,
        as_user=True
    )


def make_message(command):
    return texts.get(command, "message not defined")


def eval_command(command):
    return {
        "start": start,
        "down": down,
        "harddrop": harddrop,
        "left": left,
        "right": right,
        "turn": turn,
        "stop": stop
    }.get(command)()


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


@RTMClient.run_on(event='message')
def handle_message(**event_data):
    message = event_data.get("data")
    mentions = [BOT_NAME, "<@%s>" % BOT_ID]
    if message.get("text") and message["text"].split()[0] in mentions:
        commands = parse_commands(message["text"].split()[1:])
        channel = message["channel"]
        message_text = ""
        for i, command in enumerate(commands):
            if not tetris.player:
                tetris.player = message["ts"]

            try:
                if command == "start":
                    if tetris.playing:
                        message_text = make_message("playing")
                    else:
                        eval_command(command)
                        message_text = make_message(command)
                        message_text += "\n"
                        message_text += get_playground()
                else:
                    if tetris.playing:
                        if eval_command(command):
                            message_text = make_message(command)
                            message_text += "\n"
                            message_text += get_playground()
                        else:
                            message_text = make_message("cannot_move")
                            message_text += "\n"
                            message_text += get_playground()
                    else:
                        message_text = make_message("not_playing")
            except Exception as e:
                logger.warn(e)
                message_text = make_message("help")

            if i + 1 == len(commands) or command != commands[i + 1]:
                post_message(channel, message_text)


if __name__ == "__main__":
    # start rtm client
    rtmclient.start()
