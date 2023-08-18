
from flask import Flask, abort, request, jsonify
from tempfile import NamedTemporaryFile
# import whisper
import whisper_timestamped as whisper

import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)

loaded_model = None  # Global variable to store the loaded model

@app.route('/api/whisper/ping')
def ping():
    return "pong"

@app.route('/api/whisper/load_model', methods=['POST'])
def load_model():
    global loaded_model
    
    # if loaded_model:
    #     return jsonify({'message': 'Model is already loaded'}), 200

    data = request.json  # Expecting JSON data with 'model_name' and 'device'
    
    if 'model_name' not in data or 'device' not in data:
        return jsonify({'error': 'Missing model_name or device'}), 400

    model_name = data['model_name']
    device = data['device']

    available_devices = ['cuda', 'cpu']
    if device not in available_devices:
        return jsonify({'error': 'Invalid device'}), 400
    
    try:
        loaded_model = whisper.load_model(model_name, device=device)
    except Exception as e:
        return jsonify({'error': f'Error loading model: {str(e)}'}), 500

    return jsonify({'message': f'Model {model_name} loaded on {device}'}), 200

@app.route('/api/whisper/transcribe', methods=['POST'])
def handler():
    results = []
    model_name = request.form['model_name']
    device = request.form['device']
    loaded_model = whisper.load_model(model_name, device=device)

    # Handle uploaded files
    for filename, handle in request.files.items():
        temp = NamedTemporaryFile()
        handle.save(temp)

        # if not loaded_model:
        #     return jsonify({'error': 'Model not loaded'}), 500
        if 'model_name' not in request.form or 'device' not in request.form:
            return jsonify({'error': 'Missing model_name or device'}), 400
        # if not loaded_model:
        #     return jsonify({'error': 'Model not loaded'}), 500
        audio = whisper.load_audio(temp.name)
        result = whisper.transcribe(loaded_model, audio)
        
        # result = loaded_model.transcribe(temp.name)
        results.append({
            'filename': filename,
            'transcript': result,
        })

    # Handle video file URLs
    if 'video_url' in request.form:
        video_url = request.form['video_url']
        response = requests.get(video_url, stream=True)

        if response.status_code == 200:
            filename = secure_filename(video_url.split("/")[-1])
            temp = NamedTemporaryFile(delete=False)
            temp.write(response.content)
            temp.close()
            # write same stuff as above
            audio = whisper.load_audio(temp.name)
            result = whisper.transcribe(loaded_model, audio)
            results.append({
                'filename': filename,
                'transcript': result,
            })
        else:
            return jsonify({'error': 'Failed to download video'}), 500

    return {'results': results}

if __name__ == "__main__":
    # Load the 'base' model by default
    try:
        loaded_model = whisper.load_model('base', device='cpu')
        
        print("Default model 'base' loaded successfully.")
    except Exception as e:
        print(f"Error loading default model: {str(e)}")

    app.run(host='0.0.0.0', port=3000)
