from flask import Flask, Response, json, redirect, request
from simple_websocket import Server, ConnectionClosed
import time, uuid, msgpack, base64
class Room:
  def __init__(self, room_id):
    self.room = room_id
    self.connections = []

  async def broadcast(self, message, sender):
    for connection in self.connections:
      print(message)
      await connection.send(message)

room_dict = {}

hunterId = ""
userId = uuid.uuid4().hex
userId = userId[:8] + "-" + userId[8:12] + "-" + userId[12:16] + "-" + userId[16:20] + "-" + userId[20:]

app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello World!"

# register system

@app.route("/systems/EAR-B-WW/00001/system.json")
def system():
    host = request.host
    resp = Response()
    resp.data = json.dumps(
        {
            "api_timeout":   30000,
            "custom_property": 
                base64.b64encode(
                    bytes(
                        json.dumps(
                            {
                                "obt_info" :
                                    {
                                        "env":       1,
                                        "start_time": 1730428200,
                                        "end_time":   int(time.time()) + 114514,
                                    },
                                "qa3" :
                                    {
                                        "api":    "https://" + host,
                                        "notify": "wss://" + host,
                                    }
                            }
                        ), "utf-8"
                    )
                ).decode("utf-8")
            ,
			"json_ver":      "1.0.2",
			"mmr":          "https://mmr.rebe.capcom.com",
			"mtm":          "https://" + host,
			"mtms":         "https://mtms.rebe.capcom.com",
			"nkm":          "https://nkm.rebe.capcom.com",
			"revision":     "00001",
			"selector":     "https://selector.gs.capcom.com",
			"title":        "EAR-B-WW",
			"tmr":          "https://" + host + "/v1/projects/earth-analysis-obt/topics/analysis-client-log:publish",
			"wlt":          "https://wlt.rebe.capcom.com",
			"working_state": "alive",
		}
    )
    resp.content_type = "application/json; charset=utf-8"
    return resp

@app.route("/consents/EAR-B-WW/analysis/1/zh-hans.json")
def consents():
    resp = Response()
    resp.data = open("json/zh-hans.json").read()
    resp.content_type = "application/json; charset=utf-8"
    return resp

# @app.route("/consents/EAR-B-WW/analysis/1/en.json")
# def consents_en():
#     resp = Response()
#     resp.json = json.load(open("json/en.json"))
#     return resp

# register listpartyqosservers

@app.route("/MultiplayerServer/ListPartyQosServers")
def ListPartyQosServers():
    resp = Response()
    resp.data = open("json/list_party_qos_servers.json").read()
    resp.content_type = "application/json; charset=utf-8"
    return resp

# register v1 api

@app.route("/v1/steam-steam/sign/EAR-B-WW", methods=["POST"])
def sign():
    resp = Response()
    resp.data = open("json/steam_sign_ear-b-ww.json").read()
    resp.content_type = "application/json; charset=utf-8"
    return resp

@app.route("/v1/consent/restrictions/<country_code>")
def restrictions(country_code):
    resp = Response()
    resp.data = open("json/restrictions.json").read()
    resp.content_type = "application/json; charset=utf-8"
    return resp

@app.route("/v1/consent/countries/<country_code>")
def countries(country_code):
    resp = Response()
    resp.data = open("json/countries.json").read()
    resp.content_type = "application/json; charset=utf-8"
    return resp

@app.route("/v1/consent/documents/EAR-B-WW/<restriction>/<lang>/<tail>")
def earbww(restriction, lang, tail):
    resp = Response()
    resp.data = open("json/over.json").read()
    resp.content_type = "application/json; charset=utf-8"
    return resp

@app.route("/v1/projects/<junk1>/<junk2>/<junk3>", methods=["POST"])
def projects(junk1, junk2, junk3):
    resp = Response()
    resp.data = open("json/projects.json").read()
    resp.content_type = "application/json; charset=utf-8"
    return resp

@app.route("/v1/token/refresh/")
def token():
    resp = Response()
    resp.data = open("json/refresh.json").read()
    resp.content_type = "application/json; charset=utf-8"
    return resp

# register auth

@app.route("/auth/login", methods=["POST"])
def login():
    resp = Response()
    session = uuid.uuid4().hex
    session = session[:8] + "-" + session[8:12] + "-" + session[12:16] + "-" + session[16:20] + "-" + session[20:]
    data = {
        "SessionId":        session,
        "UserId":           userId,
        "IsInCommunityBan": False,
    }
    resp.data = msgpack.packb(data)
    nonce = uuid.uuid4().hex
    nonce = nonce[:8] + "-" + nonce[8:12] + "-" + nonce[12:16] + "-" + nonce[16:20] + "-" + nonce[20:]
    resp.headers["x-session-nonce"] = nonce
    resp.content_type = "application/octet-stream"
    return resp

@app.route("/auth/ticket", methods=["POST"])
def ticket():
    resp = Response()
    ticket = uuid.uuid4().hex
    ticketf = ticket[:8] + "-" + ticket[8:12] + "-" + ticket[12:16] + "-" + ticket[16:20] + "-" + ticket[20:]
    resp.data = bytes("\x81\xa6" + "Ticket" + "\xd9\x24" + ticketf, encoding="latin-1")
    nonce = uuid.uuid4().hex
    nonce = nonce[:8] + "-" + nonce[8:12] + "-" + nonce[12:16] + "-" + nonce[16:20] + "-" + nonce[20:]
    resp.headers["x-session-nonce"] = nonce
    resp.content_type = "application/octet-stream"
    return resp

# register others

@app.route("/delivery_data/get", methods=["POST"])
def delivery_data():
    resp = Response()
    file = open("json/delivery_data_get.bin", "rb")
    resp.data = file.read()
    nonce = uuid.uuid4().hex
    nonce = nonce[:8] + "-" + nonce[8:12] + "-" + nonce[12:16] + "-" + nonce[16:20] + "-" + nonce[20:]
    resp.headers["x-session-nonce"] = nonce
    resp.content_type = "application/octet-stream"
    return resp

@app.route("/hunter/sync", methods=["POST"])
def sync():
    global hunterId
    body = request.get_data()
    bdata = msgpack.unpackb(body)
    print(bdata)
    savelist = bdata["HunterSaveList"]
    print(savelist)
    hid = savelist[0]["HunterId"]
    if hid == b"":
        hid = uuid.uuid4().hex
        hid = hunterId[:8] + "-" + hunterId[8:12] + "-" + hunterId[12:16] + "-" + hunterId[16:20] + "-" + hunterId[20:]
    hunterId = hid
    resp = Response()
    resp.data = msgpack.packb(
        {
            "InvalidSaveSlotInfoList":   None,
            "InvalidClientHunterIdList": None,
			"SaveSlotInfoList": [
				{
					"HunterInfo": {
						"HunterId":   hunterId,
						"HunterName": savelist[0]["HunterName"],
						"OtomoName":  savelist[0]["OtomoName"],
						"SaveSlot":   0,
					},
					"ShortId": "1A2B3C4D",
				},
			]
        }
    )
    nonce = uuid.uuid4().hex
    nonce = nonce[:8] + "-" + nonce[8:12] + "-" + nonce[12:16] + "-" + nonce[16:20] + "-" + nonce[20:]
    resp.headers["x-session-nonce"] = [nonce]
    resp.content_type = "application/octet-stream"
    return resp

@app.route("/hunter/character_creation/upload", methods=["POST"])
def upload():
    resp = Response()
    resp.data = msgpack.packb(
        {
			"UploadUrl": "https://hjm.rebe.capcom.com/character-creation/b9/" + userId,
			"SignedHeaders": [
				{
					"HeaderKey":    "Host",
					"HeaderValues": ["hjm.rebe.capcom.com"],
				}, {
					"HeaderKey":    "Content-Length",
					"HeaderValues": ["3"],
				},
            ],
		}
    )
    nonce = uuid.uuid4().hex
    nonce = nonce[:8] + "-" + nonce[8:12] + "-" + nonce[12:16] + "-" + nonce[16:20] + "-" + nonce[20:]
    resp.headers["x-session-nonce"] = nonce
    resp.content_type = "application/octet-stream"
    return resp

@app.route("/hunter/profile/update", methods=["POST"])
def update():
    resp = Response()
    resp.data = msgpack.packb(
        {
			"UploadUrl": "https://hjm.rebe.capcom.com/hunter-profile/dd/" + hunterId,
			"SignedHeaders": [
				{
					"HeaderKey":    "Host",
					"HeaderValues": ["hjm.rebe.capcom.com"],
				}, {
					"HeaderKey":    "Content-Length",
					"HeaderValues": ["14113"],
				},
			],
		}
    )
    nonce = uuid.uuid4().hex
    nonce = nonce[:8] + "-" + nonce[8:12] + "-" + nonce[12:16] + "-" + nonce[16:20] + "-" + nonce[20:]
    resp.headers["x-session-nonce"] = nonce
    resp.content_type = "application/octet-stream"
    return resp

@app.route("/hunter/update/rank", methods=["POST"])
def rank():
    data = {
    }
    resp = Response()
    resp.data = msgpack.packb(data)
    nonce = uuid.uuid4().hex
    nonce = nonce[:8] + "-" + nonce[8:12] + "-" + nonce[12:16] + "-" + nonce[16:20] + "-" + nonce[20:]
    resp.headers["x-session-nonce"] = nonce
    resp.content_type = "application/octet-stream"
    return resp

@app.route("/obt/play", methods=["POST"])
def play():
    data = b"\x80"
    resp = Response()
    resp.data = data
    nonce = uuid.uuid4().hex
    nonce = nonce[:8] + "-" + nonce[8:12] + "-" + nonce[12:16] + "-" + nonce[16:20] + "-" + nonce[20:]
    resp.headers["x-session-nonce"] = nonce
    resp.content_type = "application/octet-stream"
    return resp

@app.route("/character-creation/<junk1>/<junk2>", methods=["PUT"])
def creation(junk1, junk2):
    resp = Response()
    resp.data = bytes("", encoding="latin-1")
    resp.content_type = ""
    return resp

@app.route("/hunter-profile/<junk1>/<junk2>", methods=["PUT"])
def profile(junk1, junk2):
    resp = Response()
    resp.data = bytes("", encoding="latin-1")
    resp.content_type = ""
    return resp

# register ingame

@app.route("/follow/total_list", methods=["POST"])
def total_list():
    resp = Response()
    resp.data = msgpack.packb(
        {
			"FollowList":      [],
			"LastOperationId": "",
		}
    )
    nonce = uuid.uuid4().hex
    nonce = nonce[:8] + "-" + nonce[8:12] + "-" + nonce[12:16] + "-" + nonce[16:20] + "-" + nonce[20:]
    resp.headers["x-session-nonce"] = nonce
    resp.content_type = "application/octet-stream"
    return resp

@app.route("/offline/notification_list", methods=["POST"])
def notification_list():
    resp = Response()
    resp.data = msgpack.packb(
        {
			"List": []
		}
    )
    nonce = uuid.uuid4().hex
    nonce = nonce[:8] + "-" + nonce[8:12] + "-" + nonce[12:16] + "-" + nonce[16:20] + "-" + nonce[20:]
    resp.headers["x-session-nonce"] = nonce
    resp.content_type = "application/octet-stream"
    return resp

@app.route("/community/invitation/received_list", methods=["POST"])
def received_list():
    resp = Response()
    resp.data = msgpack.packb(
        {
			"List": []
		}
    )
    nonce = uuid.uuid4().hex
    nonce = nonce[:8] + "-" + nonce[8:12] + "-" + nonce[12:16] + "-" + nonce[16:20] + "-" + nonce[20:]
    resp.headers["x-session-nonce"] = nonce
    resp.content_type = "application/octet-stream"
    return resp

@app.route("/block/list", methods=["POST"])
def block_list():
    resp = Response()
    resp.data = msgpack.packb(
        {
			"IsConsistent":  True,
			"BlockedHunter": [],
			"OperationId":   0,
		}
    )
    nonce = uuid.uuid4().hex
    nonce = nonce[:8] + "-" + nonce[8:12] + "-" + nonce[12:16] + "-" + nonce[16:20] + "-" + nonce[20:]
    resp.headers["x-session-nonce"] = nonce
    resp.content_type = "application/octet-stream"
    return resp

@app.route("/friend/list", methods=["POST"])
def friend_list():
    resp = Response()
    resp.data = msgpack.packb(
        {
			"FriendList": []
		}
    )
    nonce = uuid.uuid4().hex
    nonce = nonce[:8] + "-" + nonce[8:12] + "-" + nonce[12:16] + "-" + nonce[16:20] + "-" + nonce[20:]
    resp.headers["x-session-nonce"] = nonce
    resp.content_type = "application/octet-stream"
    return resp

@app.route("/lobby/auto_join", methods=["POST"])
def auto_join():
    resp = Response()
    resp.data = msgpack.packb(
        {
            "Endpoints": ["hjm.rebe.capcom.com:443"]
        }
    )
    nonce = uuid.uuid4().hex
    nonce = nonce[:8] + "-" + nonce[8:12] + "-" + nonce[12:16] + "-" + nonce[16:20] + "-" + nonce[20:]
    resp.headers["x-session-nonce"] = nonce
    resp.content_type = "application/octet-stream"
    return resp

# register wss handler

@app.route("/ws", websocket = True)
def ws_handler():
    ws = Server.accept(request.environ, subprotocols=["access_token"])
    print("Connected in ws")
    try:
        while(True):
            data = ws.receive()
            if data is None:
                break
            print("WS:", data)
    except ConnectionClosed:
        print("Disconnected ws")
    ws.close()
    return ''

@app.route("/socket", websocket = True)
def socket_handler():
    ws = Server.accept(request.environ, subprotocols=["access_token"])
    print("Connected in socket")
    message1 = bytes("\x81\x01\x00\x00"+ hunterId + userId, encoding="latin-1")
    ws.send(message1)

    message2 = bytes("\x85\x00\x02\x01\x01\x63\x00\x00\x00"+"FAKENAME", encoding="latin-1")
    ws.send(message2)

    try:
        for i in range(8):
            data = ws.receive()
            if data is None:
                break
            print("SOCKET:", data)
    except ConnectionClosed:
        print("Disconnected socket")
    ws.close()
    return ''

if __name__ == "__main__":
    app.run(ssl_context=('cert/website.crt', 'cert/website.key'), port=443, host="0.0.0.0")