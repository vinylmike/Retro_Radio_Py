from flask import Flask, render_template, redirect, url_for
import os
import subprocess

# Set up Flask with custom template and static folders
app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# Folder with your music files
MUSIC_FOLDER = "/mnt/share/Pi_Music"

# MPV subprocess and current track tracking
mpv_process = None
current_track = None

# Get list of music files in the folder
def get_music_files():
    return sorted([
        f for f in os.listdir(MUSIC_FOLDER)
        if f.lower().endswith(('.mp3', '.wav', '.flac'))
    ])

# Play a selected track using USB audio output (card 3)
def play_track(filename):
    global mpv_process, current_track
    stop_track()
    filepath = os.path.join(MUSIC_FOLDER, filename)
    mpv_process = subprocess.Popen(
        ["mpv", "--no-terminal", "--volume=70", "--audio-device=alsa/plughw:3,0", filepath],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )
    current_track = filename

# Stop currently playing track
def stop_track():
    global mpv_process
    if mpv_process:
        mpv_process.terminate()
        mpv_process = None

# Main page route
@app.route("/")
def index():
    tracks = get_music_files()
    return render_template("index.html", tracks=tracks, current=current_track)

# Play a track route
@app.route("/play/<filename>")
def play(filename):
    play_track(filename)
    return redirect(url_for("index"))

# Stop playback route
@app.route("/stop")
def stop():
    stop_track()
    return redirect(url_for("index"))

# Launch the web app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
