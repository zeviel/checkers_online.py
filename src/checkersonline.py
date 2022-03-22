import socket
from sys import stderr
from hashlib import md5
from loguru import logger
from threading import Thread
from base64 import b64encode
from datetime import datetime
from json import dumps, loads


class CheckersClient:
    def __init__(
        self,
        token: str = None,
        platform: str = "android",
        debug: bool = False,
        language: str = "ru",
        tag: str = "client"
    ):
        self.platform = platform
        self.tag = tag.upper()
        self.language = language
        self.user_id = None
        self.logger = logger
        self.create_connection()
        self.logger.remove()
        self.logger.add(
            stderr,
            format="{time:HH:mm:ss.SSS}:{message}",
            level="DEBUG" if debug else "INFO",
        )
        self.sign(self.get_session_key())
        if token:
            self.signin_by_access_token(token)

    def create_connection(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(("65.21.247.72", 12771))
        self.logger.info(f"Connected to the server!")

    def send_server(self, data: dir):
        self.socket.send(
            (data.pop("command") +
             dumps(
                data,
                separators=(
                    ",",
                    ":")).replace(
                "{}",
                "") +
                "\n").encode())

    def receive_server_response(self, unmarshal: bool = False):
        if unmarshal:
            return self.unmarshal(self.socket.recv(4096).decode())
        else:
            return self.socket.recv(4096).decode()

    def unmarshal(self, data: dir):
        result = [{}]
        for i in data.strip().split("\n"):
            position = i.find("{")
            command = i[:position]
            try:
                message = loads(i[position:])
            except BaseException:
                pass
                continue
            message["command"] = command
            result.append(message)
        return result[1:] if len(result) > 1 else result

    def get_session_key(self):
        data = {
            "tz": "+03:00",
            "t": f"{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}Z",
            "l": self.language,
            "p": 11,
            "pl": self.platform,
            "d": "Asus ASUS_Z01QD",
            "v": "1.1.2",
            "n": "che.android",
            "and": 25,
            "command": "c",
        }
        self.send_server(data)
        data = self.receive_server_response()
        self.logger.debug(data)
        return self.unmarshal(data)[0]["key"]

    def sign(self, session_key: int):
        hash = b64encode(
            md5(
                (
                    f"{session_key}falgcanfxehkufvcukydbvkudvgkuydsdasfdfvwvcyksed"
                ).encode()
            ).digest()
        ).decode()
        self.send_server({"hash": hash, "command": "sign"})
        self.logger.debug(self.receive_server_response())
        self.logger.info(f"[{self.tag}] Session is verified!")

    def signin_by_access_token(self, token: str):
        self.token = token
        self.send_server({"token": self.token, "command": "auth"})
        data = self.receive_server_response(unmarshal=True)
        self.user_id = self.get_authorized()[0]["id"]
        self.logger.debug(data)
        self.logger.info(
            f"[{self.tag}] Authorized with::: {self.token} successful!")
        return data

    def join_to_game(self, game_id: int, password: str = None):
        if password:
            data = {"password": password, "id": game_id, "command": "join"}
        else:
            data = {"id": game_id, "command": "join"}
        self.send_server(data)

    def leave_from_game(self, game_id: int):
        self.send_server({"id": game_id, "command": "leave"})

    def ready(self):
        self.send_server({"command": "ready"})

    def surrender(self):
        self.send_server({"command": "surrender"})

    def create_game(
            self,
            type: int = 1,
            bet: int = 100,
            password: str = None,
            fast: bool = True):
        if password:
            data = {
                "type": type,
                "password": password,
                "bet": bet,
                "fast": fast}
        else:
            data = {"type": type, "bet": bet, "fast": fast}
        self.send_server(data)

    def lookup_start(
        self,
        type: list = [1, 2],
        pr: bool = False,
        cube: list = [False, True],
        fast: list = [False, True],
        bet_min: int = 100,
        bet_max: int = 1000,
        full: bool = False
    ):
        self.send_server(
            {
                "command": "lookup_start",
                "type": type,
                "pr": [pr],
                "cube": cube,
                "fast": fast,
                "betMin": bet_min,
                "betMax": bet_max,
                "full": [full],
            }
        )

    def lookup_stop(self):
        self.send_server({"command": "lookup_stop"})

    def update_nickname(self, nickname: str = None):
        self.send_server(
            {"command": "update_name", "value": nickname}, receive=True)

    def send_smile_in_game(self, smile_id: int = 7):
        self.send_server({"command": "smile", "id": smile_id})

    def get_captcha(self):
        self.send_server({"command": "get_captcha"})
        return self.receive_server_response(unmarshal=True)

    def buy_premium(self, id: int = 0):
        self.send_server({"command": "buy_prem",
                          "id": f"com.rstgames.che.prem.{id}"})

    def buy_points(self, id: int = 0):
        self.send_server(
            {"command": "buy_points", "id": f"com.rstgames.che.points.{id}"}
        )

    def search_user(self, nickname: str):
        self.send_server({"command": "users_find", "name": nickname})
        return self.receive_server_response(unmarshal=True)

    def send_friend_request(self, user_id: int):
        self.send_server({"command": "friend_request", "id": user_id})

    def cancel_friend_request(self, user_id: int):
        self.send_server({"command": "friend_decline", "id": user_id})

    def get_user_info(self, user_id: int):
        self.send_server({"command": "get_user_info", "id": user_id})
        return self.receive_server_response(unmarshal=True)

    def save_note(self, user_id: int, note: str, color: int = 0):
        self.send_server(
            {"command": "save_note", "id": user_id, "color": color, "note": note}
        )

    def get_purchase_ids(self):
        self.send_server({"command": "get_android_purchase_ids"})
        return self.receive_server_response(unmarshal=True)

    def get_prem_price(self):
        self.send_server({"command": "get_prem_price"})
        return self.receive_server_response(unmarshal=True)

    def get_points_price(self):
        self.send_server({"command": "get_points_price"})
        return self.receive_server_response(unmarshal=True)

    def get_bets(self):
        self.send_server({"command": "gb"})
        return self.receive_server_response(unmarshal=True)

    def get_assets(self):
        self.send_server({"command": "get_assets"})
        return self.receive_server_response(unmarshal=True)

    def asset_select(self, asset_id: int):
        self.send_server({"command": "asset_select", "id": asset_id})

    def achieve_select(self, achieve_id: int):
        self.send_server({"command": "achieve_select", "id": achieve_id})

    def get_friends_list(self):
        self.send_server({"command": "friends_list"})
        return self.receive_server_response(unmarshal=True)

    def get_authorized(self):
        self.send_server({"command": "authorized"})
        return self.receive_server_response(unmarshal=True)

    def invite_to_game(self, user_id: int):
        self.send_server({"command": "invite_to_game", "user_id": user_id})

    def send_user_message(self, user_id: int, message: str):
        self.send_server({"command": "send_user_msg",
                         "to": user_id, "msg": message})

    def delete_messege(self, message_id: int):
        self.send_server({"command": "delete_msg", "msg_id": message_id})

    def accept_friend(self, user_id: int):
        self.send_server({"command": "friend_accept", "id": user_id})

    def delete_friend(self, user_id: int):
        self.send_server({"command": "friend_delete", "id": user_id})

    def send_draw_request(self):
        self.send_server({"command": "draw_request"})
