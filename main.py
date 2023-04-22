from flask import Flask, render_template, request
from flask_socketio import SocketIO, send
import folium
from DataHandler.DataHandler import DataHandler

app = Flask(__name__)
app.config["SECRET_KEY"] = "very_secretno"

socket = SocketIO(app, cors_allowed_origins="*")

@socket.on("processing_done")
def check_file(data):
    print(data["data"])
    send(data)

main_html = "site.html"

@app.route("/map")
def render_map():
    m = folium.Map()
    tooltip = "Click me!"
    folium.Marker([45.3288, -121.6625], popup="<i>Mt. Hood Meadows</i>", tooltip=tooltip).add_to(m)
    return m.get_root().render()

working_id = set()
deleted_id = set()

def get_id():
    if len(working_id)==0:
        working_id.add(0)
        return 0
    if len(deleted_id)==0:
        if min(working_id) == 0:
            working_id.add(max(working_id)+1)
            return max(working_id)
        else:
            working_id.add(min(working_id)-1)
            return min(working_id)
    ret = min(deleted_id)
    deleted_id.discard(ret)
    working_id.add(ret)
    return ret

def del_id(i):
    if i != max(working_id) and i != min(working_id):
        deleted_id.add(i)
    working_id.discard(i)

@app.route("/", methods=["POST", "GET"])
def first_page():
    if request.method == "POST":
        f = request.files["file"]
        id = get_id()
        f.save("files/"+str(id))
        return render_template(main_html, scroll="true", id = str(id))
    else:
        return render_template(main_html, scroll="false")

@app.route("/test")
def test_page():
    return render_template("test.html")

if __name__ == '__main__':
    socket.run(app)