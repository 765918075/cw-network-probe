import os
import socket
import ssl
import time
import websocket

from flask import Flask, jsonify

app = Flask(__name__)

HOST = "dhyaoj-gate.khlgamen.com"
GAME_PORT = 443
URL = "wss://dhyaoj-gate.khlgamen.com/ws"


def probe():
    result = {}

    try:
        infos = socket.getaddrinfo(
            HOST,
            GAME_PORT,
            type=socket.SOCK_STREAM,
        )
        result["dns"] = {
            "ok": True,
            "ips": sorted({x[4][0] for x in infos}),
        }
    except Exception as e:
        result["dns"] = {
            "ok": False,
            "error": f"{type(e).__name__}: {e}",
        }
        return result

    try:
        t = time.time()
        sock = socket.create_connection(
            (HOST, GAME_PORT),
            timeout=10,
        )
        result["tcp443"] = {
            "ok": True,
            "peer": str(sock.getpeername()),
            "seconds": round(time.time() - t, 3),
        }
    except Exception as e:
        result["tcp443"] = {
            "ok": False,
            "error": f"{type(e).__name__}: {e}",
        }
        return result

    try:
        ctx = ssl.create_default_context()
        t = time.time()
        tls = ctx.wrap_socket(
            sock,
            server_hostname=HOST,
        )
        result["tls"] = {
            "ok": True,
            "version": tls.version(),
            "seconds": round(time.time() - t, 3),
        }
        tls.close()
    except Exception as e:
        result["tls"] = {
            "ok": False,
            "error": f"{type(e).__name__}: {e}",
        }
        return result

    try:
        t = time.time()
        ws = websocket.create_connection(
            URL,
            timeout=10,
        )
        result["wss"] = {
            "ok": True,
            "seconds": round(time.time() - t, 3),
        }
        ws.close()
    except Exception as e:
        result["wss"] = {
            "ok": False,
            "error": f"{type(e).__name__}: {e}",
        }

    return result


@app.route("/")
def index():
    return jsonify(probe())


@app.route("/healthz")
def healthz():
    return jsonify({"ok": True})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "3000"))
    app.run(host="0.0.0.0", port=port)
