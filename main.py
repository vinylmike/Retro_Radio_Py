from flask import Flask, render_template, redirect, url_for
import os
import subprocess
import socket
import json
import time

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

MUSIC_FOLDER = "/mnt/share/Pi_Music"
mpv_process = None
current_track = None
track_list = []
current_index = -1
volume_level = 70
ipc_socket_path = "/tmp/mpv-socket"

def get_music_files():
    return sorted([
        f for f in os.listdir(MUSIC_FOLDER)
        if f.lower().endswith(('.mp3', '.wav', '.flac'))
    ])

def send_mpv_command(command_dict):
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(ipc_socket_path)
        client.send((json.dumps(command_dict) + '\n').encode())
        client.close()
    except Exception as e:
        print(f"[MPV IPC ERROR] {e}")

def play_track_by_index(index):
    global current_index, track_list
    if 0 <= index < len(track_list):
        current_index = index
        play_track(track_list[index])

def play_track(filename):
    global mpv_process, current_track, track_list, current_index
    stop_track()
    filepath = os.path.join(MUSIC_FOLDER, filename)
    if filename in track_list:
        current_index = track_list.index(filename)

    cmd = [
        "mpv",
        "--no-terminal",
        f"--volume={volume_level}",
        "--audio-device=alsa/plughw:3,0",
        f"--input-ipc-server={ipc_socket_path}",
        filepath
    ]

    mpv_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    current_track = filename

    # Wait briefly for socket to be ready
    for _ in range(10):
        if os.path.exists(ipc_socket_path):
            break
        time.sleep(0.1)

def stop_track():
    global mpv_process
    if mpv_process:
        send_mpv_command({"command": ["quit"]})
        mpv_process = None
    if os.path.exists(ipc_socket_path):
        os.remove(ipc_socket_path)

@app.route("/")
def index():
    global track_list
    track_list = get_music_files()
    return render_template("index.html", tracks=track_list, current=current_track, volume=volume_level)

@app.route("/play/<filename>")
def play(filename):
    play_track(filename)
    return redirect(url_for("index"))

@app.route("/stop")
def stop():
    stop_track()
    return redirect(url_for("index"))

@app.route("/next")
def next_track():
    if track_list:
        next_index = (current_index + 1) % len(track_list)
        play_track_by_index(next_index)
    return redirect(url_for("index"))

@app.route("/prev")
def prev_track():
    if track_list:
        prev_index = (current_index - 1) % len(track_list)
        play_track_by_index(prev_index)
    return redirect(url_for("index"))

@app.route("/set_volume/<int:level>")
def set_volume(level):
    global volume_level
    volume_level = max(0, min(100, level))
    send_mpv_command({"command": ["set_property", "volume", volume_level]})
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
