from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import re
import csv
import os

# New: Sentence embedding
from sentence_transformers import SentenceTransformer, util
import torch
app = Flask(__name__)

# Only allow requests from specific frontends and allow credentials
CORS(app, supports_credentials=True, origins=[
    "http://localhost:3000",
    "https://bim-translator-app-537545827003.asia-southeast1.run.app",
    "https://bim-translator-l4md.vercel.app"
])

ANIMATION_FOLDER = "animation-sequence-by-word"

print("Loading sentence transformer model...")
embedding_model = SentenceTransformer('/app/models/paraphrase-MiniLM-L6-v2')
print("Model loaded.")

known_animations = {
    "apa nama": ["Apa.csv", "Nama.csv"],
    "pekerjaan apa": ["Pekerjaan.csv", "Apa.csv"],
    "berapa tinggi": ["Berapa.csv", "Tinggi.csv"]
}

known_occupations = [
    "Doctor", 
    "Jurutera", 
    "Chef", 
    "Cikgu", 
    "Jururawat",
    "Ahli Sukan",
    "Menteri",
    "Wartawan",
    "Penjawat Awam",
    "Saintis",
    "Polis",
    "Bomba",
    "Askar",
    "Guru",
    "Akauntan",
    "Ahli Usahawan"
    ]

animation_keys = list(known_animations.keys())
animation_embeddings = embedding_model.encode(animation_keys, convert_to_tensor=True)
occupation_embeddings = embedding_model.encode(known_occupations, convert_to_tensor=True)

def load_animation_sequences(files):
    animation_sequence = {}

    for filename in files:
        path = os.path.join(ANIMATION_FOLDER, filename)
        if os.path.exists(path):
            with open(path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                animation_sequence[filename] = list(reader)
        else:
            animation_sequence[filename] = None

    return animation_sequence

@app.route('/match_animation_sequence')
def match_animation_sequence():
    input_sentence = request.args.get('sentence')
    if not input_sentence:
        return jsonify({"error": "Missing 'sentence' parameter"}), 400

    # Encode input sentence
    input_embedding = embedding_model.encode(input_sentence, convert_to_tensor=True)

    # Compute cosine similarity
    cos_scores = util.cos_sim(input_embedding, animation_embeddings)[0]

    best_match_idx = torch.argmax(cos_scores).item()
    best_score = cos_scores[best_match_idx].item()
    matched_phrase = animation_keys[best_match_idx]

    if best_score >= 0.7:
        matched_file = known_animations[matched_phrase]

        if isinstance(matched_file, list):
            # multiple files, load each CSV content
            animation_sequence = load_animation_sequences(matched_file)
            return jsonify({
                "input": input_sentence,
                "matched_phrase": matched_phrase,
                "animation_sequence": animation_sequence,
                "confidence": round(best_score, 4)
            })
        else:
            # single file, just return the filename as before
            return jsonify({
                "input": input_sentence,
                "matched_phrase": matched_phrase,
                "animation_file": matched_file,
                "confidence": round(best_score, 4)
            })
    else:
        return jsonify({
            "input": input_sentence,
            "matched_phrase": None,
            "animation_file": None,
            "confidence": round(best_score, 4),
            "message": "No good match found"
        })
        
@app.route('/')
def index():
    messageString = "Final Route for this API is /health, /get_name, /translate_string and /match_animation_sequence"
    return messageString

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/get_name')
def get_name():
    return "BIMTranslator Prototype V1"

@app.route('/translate_string')
def translate_string():
    API_KEY = "sk-hwe6UCi9I0WCUOkekD16oQ"  # Replace with your actual Sea-Lion API key
    SEA_LION_URL = "https://api.sea-lion.ai/v1/chat/completions"
    MODEL_NAME = "aisingapore/Llama-SEA-LION-v3.5-8B-R"
    
    parameter_input = request.args.get('text_to_translate')
    if not parameter_input:
        return jsonify({"error": "Missing 'text_to_translate' parameter"}), 400
        
    # Step 1: Split by "STOP". Anything before stop is treated as a string
    parts = re.split(r'STOP', parameter_input)
    # Step 2: Remove the last item
    parts = parts[:-1]
    # Step 3: Keep only the first character of each remaining item
    first_chars = [part[0] for part in parts if part]  # check for non-empty part
    # Step 4: Join them back into a string
    result = ''.join(first_chars)
    
    text_to_translate = None
    prompt = "Unconstructed Prompt"

    if result.isdigit():        
        text_to_translate = f"My height is {result}"
        prompt = f"Give translation of {text_to_translate} in Malay, Thai and Vietnam language without any commentaries"
    else:
        word_embedding = embedding_model.encode(result, convert_to_tensor=True)
        # Compute similarity
        occupation_score = util.cos_sim(word_embedding, occupation_embeddings).max().item()
        if occupation_score > 0.7: 
            text_to_translate = f"My occupation is {result}"
            prompt = f"Give translation of {text_to_translate} in Malay, Thai and Vietnam language without any commentaries"
        else: 
            text_to_translate = f"My Name is {result}"
            prompt = f"Give translation of {text_to_translate} in Malay, Thai and Vietnam language without any commentaries"

    if not text_to_translate:
        return "Missing 'text_to_translate' parameter", 400
    
    headers = {
        "accept": "text/plain",
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "chat_template_kwargs": {
            "thinking_mode": "off"
        }
    }
    
    try:
        response = requests.post(SEA_LION_URL, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # Extract the translated content from the nested response
        translated_text = data['choices'][0]['message']['content'].strip()

        return jsonify({
            "original": text_to_translate,
            "translated": translated_text,
            "model": data.get("model"),
            "tokens_used": data.get("usage", {}),
            "response_id": data.get("id")
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Translation failed", "details": str(e)}), 500
    except (KeyError, IndexError):
        return jsonify({"error": "Unexpected response format", "raw_response": response.text}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)









