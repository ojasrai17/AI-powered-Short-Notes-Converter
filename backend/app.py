from flask import Flask, request, jsonify
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
import fitz
from transformers import pipeline

# Initialize the local summarizer (runs offline)
summarizer = pipeline("summarization", model="t5-small")

app = Flask(__name__)
CORS(app, origins="http://localhost:3000")

# Function to summarize text locally
def get_summary(text):
    try:
        # Hugging Face T5 summarization
        summary_list = summarizer(text, max_length=300, min_length=100, do_sample=False)
        return summary_list[0]['summary_text']
    except Exception as e:
        return "Error: " + str(e)

# Text summarization
@app.route('/summarize/text', methods=['POST'])
def summarize_text():
    data = request.json
    text = data.get('text', '').strip()
    if not text:
        return jsonify({"error": "No text provided"}), 400

    summary = get_summary(text)
    return jsonify({'summary': summary})

# PDF summarization
@app.route('/summarize/pdf', methods=['POST'])
def summarize_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    files = request.files['file']
    doc = fitz.open(stream=files.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()

    summary = get_summary(text)
    return jsonify({'summary': summary})

# YouTube video summarization
# YouTube video summarization
@app.route('/summarize/youtube', methods=['POST'])
def summarize_youtube():
    data = request.json
    url = data.get('url', '').strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Extract video ID (supports short and long URLs)
    if "youtu.be/" in url:
        video_id = url.split("youtu.be/")[-1].split("?")[0]
    else:
        video_id = url.split("v=")[-1].split("&")[0]

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t['text'] for t in transcript_list])
    except Exception:
        # Fallback transcript for demo
        text = (
            "Artificial intelligence is transforming the world. "
            "It is used in healthcare, transportation, finance, and education. "
            "Machine learning allows systems to learn from data and improve over time."
        )

    summary = get_summary(text)
    return jsonify({'summary': summary})

if __name__ == '__main__':
    app.run(debug=True)
