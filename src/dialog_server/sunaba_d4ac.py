import datetime
import urllib.request
import json
import ssl
from typing import Dict, Any
ssl._create_default_https_context = ssl._create_unverified_context


class SunabaDialog:

    def __init__(self, bot_id, init_topic_id,logger):

        self.url = "https://api-sunaba.xaiml.docomo-dialog.com/dialogue"
        self.error_response = "SUNABA接続エラー"
        self.bot_id = bot_id
        self.init_topic_id = init_topic_id
        self.logger = logger

        self.registration_url = "https://api-sunaba.xaiml.docomo-dialog.com/registration"
        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        data = {"botId": bot_id, "appKind": "sunaba", "notification": False}
        request = urllib.request.Request(self.registration_url, json.dumps(data).encode(), headers, method="POST")
        try:
            response = json.load(urllib.request.urlopen(request))
            self.logger.info(str(response))
            self.app_id = response["app_id"]
        except:
            raise Exception("registration to SUNABA failed.")
        # つまらないですか？を繰り返さないためのフラグ
        self.system_responded_to_non_utterance = False

    def _add_user_status(self, text, userStatus):
        if userStatus is None:
            return text
        else:
            user_status = '+'
            engagement = userStatus.get('engagement')
            if engagement is not None:
                user_status += '{engagement:'+engagement + '}'
            emotion = userStatus.get('emotion')
            if emotion is not None:
                user_status += '{emotion:' + emotion + '}'
            gender = userStatus.get('gender')
            if gender is not None:
                user_status += '{gender:' + gender + '}'
            age = userStatus.get('age')
            if age is not None:
                user_status += '{age:' + age + '}'
            return text + user_status

    def respond(self, user_input: Dict[str, Any]):
        """
        make response
        :param user_input: input from client
        :type user_input: json
        :return: output from dialogue server
        :rtype: json
        """

        if user_input["initial"]:
            system_output = self._initial_message(user_input)
        else:
            system_output = self._reply(user_input)
        return system_output

    def _initial_message(self, input):

        headers = {'Content-Type': 'application/json;charset=UTF-8'}
        data = {"appId": self.app_id,
                "botId": self.bot_id,
                "voiceText": "init",
                "initTalkingFlag": False,
                "initTopicId": self.init_topic_id,
                "language": "ja-JP"}
        try:
            request = urllib.request.Request(self.url, json.dumps(data).encode(), headers, method="POST")
            response = json.load(urllib.request.urlopen(request))
            system_utterance = response["systemText"]["expression"]
        except:
            system_utterance = self.error_response
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        output = {"systemUtterance": {"expression": system_utterance, "utterance": system_utterance},
                  "talkend": False,  # 対話の終わりかどうか
                  "sessionId": self.app_id,
                  "timestamp": time}
        return output

    def _reply(self, input):
        user_utterance = input['userUtterance']
        status = input["userStatus"]
        self.logger.info ("dialog_server received: " + user_utterance + " / " + str(status))
        if user_utterance == "" and self.system_responded_to_non_utterance == True:
            system_utterance = ""
        else:
            headers = {'Context-Type': 'application/json;charset=UTF-8'}
            if status is not None:
                text = self._add_user_status(user_utterance, status)
                #text = f"engagement {str(engagement)} : {user_utterance}"
                self.logger.info("sent to sunaba text: " + text)
                #userstatus =  {"engagement": str(engagement)}
                data = {"appId": self.app_id,
                    "botId": self.bot_id,
                    "voiceText": text,
                    "initTalkingFlag": False,
                    "clientData": {
                        "userStatus": status},
                    "language": "ja-JP"}
            else:
                status = {}
                text = user_utterance
                self.logger.info("sent to sunaba text: " + text)
                data = {"appId": self.app_id,
                    "botId": self.bot_id,
                    "voiceText": text,
                    "initTalkingFlag": False,
                    "language": "ja-JP"}

            try:
                request = urllib.request.Request(self.url, json.dumps(data).encode(), headers, method="POST")
                response = json.load(urllib.request.urlopen(request))
                self.logger.info("response->>> " + str(response))
                system_utterance = response["systemText"]["expression"]
            except:
                system_utterance = self.error_response
            if system_utterance in ("empty", "nomatch"):
                system_utterance = ""
            if user_utterance != "":
                self.system_responded_to_non_utterance = False
            elif system_utterance != "":
                self.system_responded_to_non_utterance = True
            self.logger.info(f"response: {system_utterance}")
            time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            output = {"systemUtterance": {"expression": system_utterance, "utterance": system_utterance},
                      "talkend": False,  # 対話の終わりかどうか
                      "sessionId": "session1",
                      "timestamp": time}
            return output

