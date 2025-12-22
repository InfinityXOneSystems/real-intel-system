from flask import Flask, request, jsonify
from router.dispatch import dispatch

app = Flask(__name__)

@app.route("/api/dispatch", methods=["POST"])
def api_dispatch():
    return dispatch(request.json)

@app.route("/health")
def health():
    return "ok", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
