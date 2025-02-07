import time
import threading
import mido
import keyboard
import os
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

MIDI_FOLDER = "midi_files"  # Folder where MIDI files are stored
os.makedirs(MIDI_FOLDER, exist_ok=True)  # Ensure folder exists

# MIDI Note-to-Key Mapping (Change these to match Vital keybinds)
NOTE_TO_KEY = {
    60: 'a',  # C4
    62: 's',  # D4
    64: 'd',  # E4
    65: 'f',  # F4
    67: 'g',  # G4
    69: 'h',  # A4
    71: 'j',  # B4
    72: 'k'  # C5
}


# 🎵 Function to Play a MIDI File 🎵
def play_midi_file(filename):
    """Reads a MIDI file and simulates key presses for Vital."""
    filepath = os.path.join(MIDI_FOLDER, filename)
    if not os.path.exists(filepath):
        return "File not found!"

    mid = mido.MidiFile(filepath)
    for msg in mid.play():
        if msg.type == 'note_on' and msg.velocity > 0:
            key = NOTE_TO_KEY.get(msg.note)
            if key:
                keyboard.press(key)
        elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
            key = NOTE_TO_KEY.get(msg.note)
            if key:
                keyboard.release(key)

    return "Playback finished."


# 🌐 Web Routes 🌐
@app.route('/')
def index():
    midi_files = [f for f in os.listdir(MIDI_FOLDER) if f.endswith('.mid')]
    return render_template('index.html', midi_files=midi_files)


@app.route('/press', methods=['POST'])
def press_key():
    key = request.form.get('key')
    keyboard.press(key)
    return '', 204


@app.route('/release', methods=['POST'])
def release_key():
    key = request.form.get('key')
    keyboard.release(key)
    return '', 204


@app.route('/play_midi', methods=['POST'])
def play_selected_midi():
    filename = request.form.get('filename')
    if filename:
        threading.Thread(target=play_midi_file, args=(filename,)).start()
        return jsonify({"message": f"Playing {filename}"}), 200
    return jsonify({"error": "No file selected"}), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
    print(f"Server running! Access your keyboard at http://<YOUR_IP>:5000")
