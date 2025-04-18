import subprocess
import json
import os

class RadioController:
    def __init__(self, station_file="stations.json"):
        self.station_file = station_file
        self.stations = self.load_stations()
        self.current_index = 0
        self.mpv_process = None

    def load_stations(self):
        if not os.path.exists(self.station_file):
            with open(self.station_file, 'w') as f:
                json.dump([], f)
        with open(self.station_file, 'r') as f:
            return json.load(f)

    def save_stations(self):
        with open(self.station_file, 'w') as f:
            json.dump(self.stations, f, indent=2)

    def play_station(self, index):
        self.stop()
        self.current_index = index
        url = self.stations[index]['url']
        print(f"🔊 Playing: {self.stations[index]['name']} ({url})")
        self.mpv_process = subprocess.Popen(
            ['mpv', '--no-video', url],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def stop(self):
        if self.mpv_process:
            print("🛑 Stopping playback")
            self.mpv_process.terminate()
            self.mpv_process.wait()
            self.mpv_process = None

    def next_station(self):
        if not self.stations:
            return
        self.current_index = (self.current_index + 1) % len(self.stations)
        self.play_station(self.current_index)

    def prev_station(self):
        if not self.stations:
            return
        self.current_index = (self.current_index - 1) % len(self.stations)
        self.play_station(self.current_index)

    def get_current_station(self):
        if self.stations:
            return self.stations[self.current_index]
        return {"name": "No Stations", "url": ""}

    def add_station(self, name, url):
        if len(self.stations) < 10:
            self.stations.append({"name": name, "url": url})
            self.save_stations()
            return True
        return False

    def remove_station(self, index):
        if 0 <= index < len(self.stations):
            self.stations.pop(index)
            self.save_stations()
            return True
        return False

    def update_station(self, index, name, url):
        if 0 <= index < len(self.stations):
            self.stations[index] = {"name": name, "url": url}
            self.save_stations()
            return True
        return False
