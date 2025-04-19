from flask import Flask, render_template, redirect, url_for
import os
import subprocess

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

MUSIC_FOLDER = "/mnt/share/Pi_Music"
mpv_process = None
current_track = None
track_list = []
current_index = -1
volume_level = 70  # Default volume

def get_music_files():
    return sorted([
        f for f in os.listdir(MUSIC_FOLDER)
        if f.lower().endswith(('.mp3', '.wav', '.flac'))
    ])

def play_track_by_index(index):
    global current_index, current_track, track_list
    if 0 <= index < len(track_list):
        current_index = index
        play_track(track_list[current_index])

def play_track(filename):
    global mpv_process, current_track, track_list, current_index
    stop_track()
    filepath = os.path.join(MUSIC_FOLDER, filename)
    if filename in track_list:
        current_index = track_list.index(filename)
    mpv_process = subprocess.Popen(
        [
            "mpv", "--no-terminal",
            f"--volume={volume_level}",
            "--audio-device=alsa/plughw:3,0",
            filepath
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    current_track = filename

def stop_track():
    global mpv_process
    if mpv_process:
        mpv_process.terminate()
        mpv_process = None

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
    if current_track:
        play_track(current_track)
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
