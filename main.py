from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess

app = Flask(__name__)

MUSIC_FOLDER = "/mnt/share/Pi_Music"
mpv_process = None
current_track = None

def get_music_files():
    return sorted([f for f in os.listdir(MUSIC_FOLDER) if f.lower().endswith(('.mp3', '.wav', '.flac'))])

def play_track(filename):
    global mpv_process, current_track
    stop_track()
    filepath = os.path.join(MUSIC_FOLDER, filename)
    mpv_process = subprocess.Popen(["mpv", filepath], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    current_track = filename

def stop_track():
    global mpv_process
    if mpv_process:
        mpv_process.terminate()
        mpv_process = None

@app.route("/")
def index():
    files = get_music_files()
    return render_template("index.html", tracks=files, current=current_track)

@app.route("/play/<filename>")
def play(filename):
    play_track(filename)
    return redirect(url_for("index"))

@app.route("/stop")
def stop():
    stop_track()
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
