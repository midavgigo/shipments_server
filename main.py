from flask import Flask, render_template, request
from flask_socketio import SocketIO, send

app = Flask(__name__)
app.config["SECRET_KEY"] = "very_secretno"

socket = SocketIO(app, cors_allowed_origins="*")

@socket.on("processing_done", namespace="/test")
def check_file(data):
    print(data)
    send(data, broadcast = True)

if __name__ == '__main__':
    socket.run(app)