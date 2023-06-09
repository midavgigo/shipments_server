from flask import Flask, render_template, request, redirect
from flask_socketio import SocketIO, emit

import folium
from DataHandler.DataHandler import DataHandler
import threading
import time
import os
import traceback
import logging

app = Flask(__name__)
app.config["SECRET_KEY"] = "very_secretno"

socket = SocketIO(app, cors_allowed_origins="*")

main_html = "site.html"

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

m = dict()

return_map = dict()

def process_file(id):
    print("start for", id)
    m[id] = folium.Map()
    dat = DataHandler("files/"+id, 10000)
    opt = dat.get_optimal_coordinates()
    try:
        folium.Marker([opt[0], opt[1]], icon=folium.Icon(color="red")).add_to(m[id])
        for i in dat.get_data_array():
            folium.Circle([float(i[0]), float(i[1])], radius=2, color="blue").add_to(m[id])
            #folium.PolyLine([(i[1], i[2]), (opt[0], opt[1])]).add_to(m[id])
        return_map[id] = 1
        return
    except ValueError:
        print("пока не знаю что делать")
        return_map[id] = 0
    except Exception as e:
        logging.error(traceback.format_exc())
        socket.emit('processing_done', "-1")
        return_map[id] = -1
        return

@socket.on("start_process")
def start_process(id):
    t1 = threading.Thread(target=process_file, args=(id), daemon=True)
    t1.start()
    t1.join()
    if return_map[id] != -1:
        print("done for", id)
        del_id(int(id))
        socket.emit('processing_done', id)
    os.remove("files/"+id)

@app.route("/map/<id>")
def render_map(id):
    try:
        temp = m[id]
        del m[id]
        return temp.get_root().render()
    except KeyError:
        return render_template(main_html, scroll="false", can_send="true")


@app.route("/", methods=["POST", "GET"])
def first_page():
    if request.method == "POST":
        f = request.files["file"]
        id = get_id()
        f.save("files/"+str(id))
        return render_template(main_html, scroll="true", id = str(id), can_send="false")
    else:
        return render_template(main_html, scroll="false", can_send="true")

@app.route("/test")
def test_page():
    return render_template("test.html")

if __name__ == '__main__':
    socket.run(app)