from flask import Flask, render_template, redirect, url_for
import os
import subprocess
import socket
import json
import time
from mutagen import File
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.easyid3 import EasyID3

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

MUSIC_FOLDER = "/mnt/share/Pi_Music"
mpv_process = None
current_track = None
track_list = []
current_index = -1
volume_level = 70
ipc_socket_path = "/tmp/mpv-socket"

# Extract metadata from audio file
def extract_metadata(filepath):
    metadata = {"filename": os.path.basename(filepath), "title": "", "artist": "", "album": "", "duration": ""}
    try:
        audio = File(filepath, easy=True)
        if audio:
            metadata["title"] = audio.get("title", [""])[0]
            metadata["artist"] = audio.get("artist", [""])[0]
            metadata["album"] = audio.get("album", [""])[0]
            if isinstance(audio, MP3) or isinstance(audio, FLAC):
                duration_sec = int(audio.info.length)
                minutes = duration_sec // 60
                seconds = duration_sec % 60
                metadata["duration"] = f"{minutes}:{seconds:02d}"
    except Exception as e:
        print(f"[Metadata Error] {filepath}: {e}")
    return metadata

def get_music_files():
    files = sorted([
        f for f in os.listdir(MUSIC_FOLDER)
        if f.lower().endswith(('.mp3', '.wav', '.flac'))
    ])
    return [extract_metadata(os.path.join(MUSIC_FOLDER, f)) for f in files]

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
        play_track(track_list[index]["filename"])

def play_track(filename):
    global mpv_process, current_track, track_list, current_index
    print(f"[DEBUG] Playing track: {filename}")  # Debugging: Print the track name
    stop_track()
    filepath = os.path.join(MUSIC_FOLDER, filename)
    print(f"[DEBUG] Filepath: {filepath}")  # Debugging: Ensure the full path is correct
    
    for i, t in enumerate(track_list):
        if t["filename"] == filename:
            current_index = i
            break

    cmd = [
        "mpv", "--no-terminal",
        f"--volume={volume_level}",
        "--audio-device=alsa/plughw:3,0",
        f"--input-ipc-server={ipc_socket_path}",
        filepath
    ]
    print(f"[DEBUG] Executing command: {cmd}")  # Debugging: Command to run in subprocess
    mpv_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    current_track = filename
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

# Function to get current time and remaining time from MPV
def get_playback_status():
    try:
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(ipc_socket_path)
        client.send((json.dumps({"command": ["get_property", "time-pos"]}) + '\n').encode())
        response = client.recv(1024).decode()
        time_pos = json.loads(response).get("data", 0)
        client.close()
        return time_pos
    except Exception as e:
        print(f"[MPV IPC Error] {e}")
        return 0

@app.route("/")
def index():
    global track_list
    track_list = get_music_files()
    now_playing_metadata = next((t for t in track_list if t["filename"] == current_track), None)
    
    current_time = get_playback_status()
    remaining_time = None
    if now_playing_metadata and current_time:
        total_seconds = int(current_time)
        remaining_time = int(now_playing_metadata["duration"]) - total_seconds

    # Add debugging for potential issues
    print("Current Track: ", current_track)
    print("Current Time: ", current_time)
    print("Remaining Time: ", remaining_time)

    return render_template(
        "index.html", 
        tracks=track_list, 
        current=now_playing_metadata if now_playing_metadata else {},
        volume=volume_level,
        current_time=current_time if current_time else 0,
        remaining_time=remaining_time if remaining_time else 0
    )

@app.route("/play/<filename>")
def play(filename):
    print(f"[DEBUG] Attempting to play file: {filename}")  # Debugging: Checking the filename
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
