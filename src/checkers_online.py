import socket
from json import dumps
from json import loads
from time import sleep
from sys import stderr
from hashlib import md5
from loguru import logger
from base64 import b64encode
from datetime import datetime


class CheckersOnline:
	def __init__(
			self,
			platform: str = "android",
			debug: bool = False,
			language: str = "ru",
			tag: str = "checkers_online".upper()) -> None:
		self.tag = tag
		self.user_id = None
		self.logger = logger
		self.language = language
		self.platform = platform
		self.create_connection()
		self.logger.remove()
		self.logger.add(
			stderr,
			format="{time:HH:mm:ss.SSS}:{message}",
			level="DEBUG" if debug else "INFO",
		)
		self.sign(self.get_session_key())

	def create_connection(self) -> str:
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect(("65.21.247.72", 12771))
		self.logger.info(f"Connected to the server!")

	def send_server(self, data: dir) -> None:
		sleep(0.1)
		self.socket.send(
			(data.pop("command") + dumps(
				data, separators=(",", ":")
			).replace("{}", "") + "\n").encode()
		)

	def receive_server_response(
			self,
			unmarshal: bool = False) -> [str, dict]:
		if unmarshal:
			return self.unmarshal(self.socket.recv(4096).decode())
		else:
			return self.socket.recv(4096).decode()

	def unmarshal(self, data: str) -> dict:
		result = [{}]
		for i in data.strip().split("\n"):
			position = i.find("{")
			command = i[:position]
			try:
				message = loads(i[position:])
			except:
				continue
			message["command"] = command
			result.append(message)
		return result[1:] if len(result) > 1 else result

	def get_session_key(self) -> str:
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
			"command": "c"
		}
		self.send_server(data)
		data = self.receive_server_response()
		return self.unmarshal(data)[0]["key"]

	def sign(self, session_key: int) -> str:
		hash = b64encode(md5(
			(
				f"{session_key}falgcanfxehkufvcukydbvkudvgkuydsdasfdfvwvcyksed").encode()
			).digest()
		).decode()
		self.send_server({"hash": hash, "command": "sign"})
		self.logger.info(f"[{self.tag}] Session is verified!")

	def login_with_access_token(self, access_token: str) -> dict:
		self.access_token = access_token
		self.send_server(
			{"token": self.access_token, "command": "auth"}
		)
		self.user_id = self.get_authorized()[0]["id"]
		self.logger.info(f"[{self.tag}] Authorized with::: {self.access_token} successful!")
		return self.receive_server_response(True)

	def join_to_game(
			self,
			game_id: int,
			password: str = None) -> None:
		data = {
			"id": game_id,
			"command": "join"
		}
		if password:
			data["password"] = password
		self.send_server(data)

	def leave_from_game(self) -> None:
		self.send_server({"command": "leave"})

	def ready(self) -> None:
		self.send_server({"command": "ready"})

	def surrender(self) -> None:
		self.send_server({"command": "surrender"})

	def create_game(
			self,
			type: int = 1,
			bet: int = 100,
			password: str = None,
			fast: bool = True) -> None:
		data = {
			"type": type,
			"bet": bet,
			"fast": fast
		}
		if password:
			data["password"] = password
		self.send_server(data)

	def lookup_start(
			self,
			type: list = [1, 2],
			pr: bool = False,
			cube: list = [False, True],
			fast: list = [False, True],
			bet_min: int = 100,
			bet_max: int = 1000000,
			full: bool = False) -> None:
		data = {
			"command": "lookup_start",
			"type": type,
			"pr": [pr],
			"cube": cube,
			"fast": fast,
			"betMin": bet_min,
			"betMax": bet_max,
			"full": [full],
		}
		self.send_server(data)

	def lookup_stop(self) -> None:
		self.send_server({"command": "lookup_stop"})

	def update_nickname(self, nickname: str) -> None:
		self.send_server({"command": "update_name", "value": nickname})

	def send_smile_in_game(self, smile_id: int) -> None:
		self.send_server({"command": "smile", "id": smile_id})

	def get_captcha(self) -> dict:
		self.send_server({"command": "get_captcha"})
		return self.receive_server_response(True)

	def buy_premium(self, id: int = 0) -> None:
		self.send_server({"command": "buy_prem", "id": f"com.rstgames.che.prem.{id}"})

	def buy_points(self, id: int = 0) -> None:
		self.send_server(
			{"command": "buy_points", "id": f"com.rstgames.che.points.{id}"})

	def search_user(self, nickname: str) -> dict:
		self.send_server({"command": "users_find", "name": nickname})
		return self.receive_server_response(True)

	def send_friend_request(self, user_id: int) -> None:
		self.send_server({"command": "friend_request", "id": user_id})

	def cancel_friend_request(self, user_id: int) -> None:
		self.send_server({"command": "friend_decline", "id": user_id})

	def get_user_info(self, user_id: int) -> dict:
		self.send_server({"command": "get_user_info", "id": user_id})
		return self.receive_server_response(True)

	def save_note(
			self,
			user_id: int,
			note: str,
			color: int = 0) -> None:
		data = {
			"command": "save_note",
			"id": user_id,
			"color": color,
			"note": note
		}
		self.send_server(data)

	def get_purchase_ids(self) -> dict:
		self.send_server({"command": "get_android_purchase_ids"})
		return self.receive_server_response(True)

	def get_premium_price(self) -> dict:
		self.send_server({"command": "get_prem_price"})
		return self.receive_server_response(True)

	def get_points_price(self) -> dict:
		self.send_server({"command": "get_points_price"})
		return self.receive_server_response(True)

	def get_bets(self) -> dict:
		self.send_server({"command": "gb"})
		return self.receive_server_response(True)

	def get_assets(self) -> dict:
		self.send_server({"command": "get_assets"})
		return self.receive_server_response(True)

	def select_asset(self, asset_id: int) -> None:
		self.send_server({"command": "asset_select", "id": asset_id})

	def select_achieve(self, achieve_id: int) -> None:
		self.send_server({"command": "achieve_select", "id": achieve_id})

	def get_friends_list(self) -> dict:
		self.send_server({"command": "friends_list"})
		return self.receive_server_response(True)

	def get_authorized(self) -> dict:
		self.send_server({"command": "authorized"})
		return self.receive_server_response(True)

	def invite_to_game(self, user_id: int) -> None:
		self.send_server({"command": "invite_to_game", "user_id": user_id})

	def send_user_message(
			self,
			user_id: int,
			message: str) -> None:
		self.send_server(
			{"command": "send_user_msg", "to": user_id, "msg": message}
		)

	def delete_messege(self, message_id: int) -> None:
		self.send_server({"command": "delete_msg", "msg_id": message_id})

	def accept_friend(self, user_id: int) -> None:
		self.send_server({"command": "friend_accept", "id": user_id})

	def delete_friend(self, user_id: int) -> None:
		self.send_server({"command": "friend_delete", "id": user_id})

	def send_draw_request(self) -> None:
		self.send_server({"command": "draw_request"})
