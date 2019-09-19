from tetris import Tetris, HEIGHT, WIDTH


class TetrisThread:
    def __init__(self, slack_client, slack_ts, slack_channel):
        # define block emojis
        self.emojis = {
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

        self.tetris = Tetris()

        self.slack_client = slack_client
        self.slack_ts = slack_ts
        self.slack_channel = slack_channel

    def start(self):
        self.tetris.playing = True
        self.tetris.clear()

    def down(self):
        success = self.tetris.down()
        if not success:
            self.tetris.player = None
            self.tetris.playing = False
        return success

    def harddrop(self):
        success = self.tetris.harddrop()
        if not success:
            self.tetris.player = None
            self.tetris.playing = False
        return success

    def left(self):
        return self.tetris.move(-1)

    def right(self):
        return self.tetris.move(1)

    def turn(self):
        return self.tetris.turn()

    def stop(self):
        self.tetris.player = None
        self.tetris.playing = False
        return True

    def get_playground(self):
        playground = ""
        for y in range(HEIGHT - 1):
            for x in range(WIDTH - 2):
                # left lane
                if x == 0:
                    playground += self.emojis[-1]

                # background or block
                b = self.tetris.block(x + 1, y)
                if b >= 1:
                    playground += self.emojis[b]
                else:
                    playground += self.emojis[0]

                # right lane
                if x == 9:
                    playground += self.emojis[-1]
                    playground += "\n"
        return playground

    def eval_command(self, command):
        return {
            "start": self.start,
            "down": self.down,
            "harddrop": self.harddrop,
            "left": self.left,
            "right": self.right,
            "turn": self.turn,
            "stop": self.stop
        }.get(command)()


    def post_message(self, text):
        self.slack_client.chat_postMessage(
            channel=self.slack_channel,
            text=text,
            thread_ts=self.slack_ts,
            as_user=True
        )
