import json
import os
import subprocess

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
        if 0 <= index < len(self.stations):
            self.current_index = index
            url = self.stations[index]['url']
            self.mpv_process = subprocess.Popen(
                ['mpv', '--no-video', url],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

    def stop(self):
        if self.mpv_process:
            self.mpv_process.terminate()
            self.mpv_process.wait()
            self.mpv_process = None

    def next_station(self):
        if self.stations:
            self.current_index = (self.current_index + 1) % len(self.stations)
            self.play_station(self.current_index)

    def prev_station(self):
        if self.stations:
            self.current_index = (self.current_index - 1) % len(self.stations)
            self.play_station(self.current_index)

    def get_current_station(self):
        if self.stations:
            return self.stations[self.current_index]
        return {"name": "No Station", "url": ""}

    def add_station(self, name, url):
        if len(self.stations) < 10:
            self.stations.append({"name": name, "url": url})
            self.save_stations()

    def remove_station(self, index):
        if 0 <= index < len(self.stations):
            del self.stations[index]
            self.save_stations()

    def update_station(self, index, name, url):
        if 0 <= index < len(self.stations):
            self.stations[index] = {"name": name, "url": url}
            self.save_stations()

    def auto_play_first(self):
        if self.stations:
            self.play_station(0)
