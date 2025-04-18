from flask import Flask, render_template, redirect, request
from radio_controller import RadioController

app = Flask(
    __name__,
    template_folder='app/templates',
    static_folder='app/static'
)

controller = RadioController()

# 🔊 Auto-play the first station on startup if any are available
if controller.stations:
    controller.play_station(0)

@app.route('/')
def index():
    stations = controller.stations
    current_station = controller.get_current_station() if stations else {"name": "No Stations", "url": ""}
    return render_template("index.html", station=current_station, stations=stations)

@app.route('/play/<int:index>')
def play(index):
    controller.play_station(index)
    return redirect('/')

@app.route('/stop')
def stop():
    controller.stop()
    return redirect('/')

@app.route('/next')
def next_station():
    controller.next_station()
    return redirect('/')

@app.route('/prev')
def prev_station():
    controller.prev_station()
    return redirect('/')

@app.route('/edit')
def edit():
    stations = controller.stations
    return render_template('edit.html', stations=stations)

@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name')
    url = request.form.get('url')
    controller.add_station(name, url)
    return redirect('/edit')

@app.route('/remove', methods=['POST'])
def remove():
    index = int(request.form.get('index'))
    controller.remove_station(index)
    return redirect('/edit')

@app.route('/update', methods=['POST'])
def update():
    index = int(request.form.get('index'))
    name = request.form.get('name')
    url = request.form.get('url')
    controller.update_station(index, name, url)
    return redirect('/edit')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
