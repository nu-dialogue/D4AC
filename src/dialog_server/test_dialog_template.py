import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from util.logger import createLogger
logger = createLogger("dummy_dialog")


class TestDialog:

    def __init__(self):

        pass

    def respond(self, user_input):

        print("user input:" + str(user_input))
        logger.info(str(user_input))
        reply: str = "こんにちは [emotion: happiness|sadness] "
        output = {"systemUtterance": {"expression": reply, "utterance": reply},
                  "talkend": False,  # 対話の終わりかどうか
                  "sessionId": "session1",
                  "timestamp": 000}
        logger.info(str(output))
        return output

