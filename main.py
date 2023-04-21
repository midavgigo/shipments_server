from flask import Flask, render_template, request
from flask_socketio import SocketIO, send
import folium

app = Flask(__name__)
app.config["SECRET_KEY"] = "very_secretno"

socket = SocketIO(app, cors_allowed_origins="*")

@socket.on("processing_done")
def check_file(data):
    print(data["data"])
    send(data, broadcast = True)

main_html = "site.html"

@app.route("/map")
def render_map():
    m = folium.Map()
    tooltip = "Click me!"
    folium.Marker([45.3288, -121.6625], popup="<i>Mt. Hood Meadows</i>", tooltip=tooltip).add_to(m)
    return m.get_root().render()

@app.route("/")
def first_page():
    return render_template(main_html)

@app.route("/upload", methods=["POST", "GET"])
def upload_file():
    if request.method == "POST":
        f = request.files["file"]
        id = request.form.get("id")
        f.save(str(id))
        return render_template(main_html)
    else:
        return render_template(main_html)

if __name__ == '__main__':
    socket.run(app)