from flask import Flask, request, send_file
from df.enhance import enhance, init_df, load_audio, save_audio
import os
from moviepy.editor import VideoFileClip
import torchaudio
from datetime import datetime

app = Flask(__name__)
model, df_state, _ = init_df()

@app.route('/uploadVideo', methods=['POST'])
def upload_file():
    print('file')
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400 

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    basename = os.path.splitext(file.filename)[0]
    temp_video_path = os.path.join('temp', f"{basename}_{timestamp}.mp4")
    file.save(temp_video_path)

    with VideoFileClip(temp_video_path) as video:
        audio_path = os.path.join('temp', f"{basename}_{timestamp}.wav")
        video.audio.write_audiofile(audio_path)
        audio, sample_rate = torchaudio.load(audio_path)
        print("Audio shape before enhancement:", audio.shape)
        enhanced = enhance(model, df_state, audio)
        print("Audio shape after enhancement:", enhanced.shape)
        enhanced_path = os.path.join('temp', f"{basename}_{timestamp}_enhanced.wav")
        save_audio(enhanced_path, enhanced, sample_rate)

    os.remove(temp_video_path)
    return send_file(enhanced_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001)
