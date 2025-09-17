from flask import Flask, request, jsonify
import requests
from flask_cors import CORS
import re
import csv
import os

# New: Sentence embedding
from sentence_transformers import SentenceTransformer, util
import torch
from rapidfuzz import fuzz, process

app = Flask(__name__)

# Only allow requests from specific frontends and allow credentials
CORS(app, supports_credentials=True, origins=[
    "http://localhost:3000",
    "https://bim-translator-app-537545827003.asia-southeast1.run.app",
    "https://bim-translator-l4md.vercel.app",
    "https://localhost:3000",
    "https://192.168.1.7:3000"
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
    "Doktor", 
    "Jurutera", 
    "Chef", 
    "Cikgu",
    "Guru",
    "Jururawat",
    "Ahli Sukan",
    "Menteri",
    "Wartawan",
    "Penjawat Awam",
    "Saintis",
    "Polis",
    "Bomba",
    "Askar",
    "Guru Besar",
    "Akauntan",
    "Ahli Usahawan",
    "Parlimen",
    "Ceo",
    "Ketua Pengarah",
    "Surirumah"
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
    messageString = "Final Route for this API is /health, /get_name, /form_answer and /match_animation_sequence"
    return messageString

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/get_name')
def get_name():
    return "AI-BIMTranslator Prototype V1"

@app.route('/form_answer')
def translate_string():
    API_KEY = "sk-CYE-0McMZfG4Qn7Jk7CClg"  # Replace with your actual Sea-Lion API key
    SEA_LION_URL = "https://api.sea-lion.ai/v1/chat/completions"
    MODEL_NAME = "aisingapore/Gemma-SEA-LION-v4-27B-IT"
    
    parameter_input = request.args.get('text_to_translate')
    if not parameter_input:
        return jsonify({"error": "Missing 'text_to_translate' parameter"}), 400

    if parameter_input.endswith("STOP"):
        result = parameter_input[:-4]
    else:
        result = parameter_input

    result = result.strip().title() 
    text_to_translate = None
    prompt = None
    matched_occupation = None
    occupation_best_score = 0
    fuzzy_score = 0

    if result.isdigit():        
        text_to_translate = f"My height is {result} cm"
        prompt = f"Give translation of {text_to_translate} in Malay, Thai and Vietnam language without any commentaries"
    else:
        match = None
        try:
            match, fuzzy_score, _ = process.extractOne(result, known_occupations, scorer=fuzz.ratio)
        except TypeError:
            pass
        word_embedding = embedding_model.encode(result, convert_to_tensor=True)
        # Compute cosine similarity between input and all occupation embeddings
        cos_scores = util.cos_sim(word_embedding, occupation_embeddings)[0]
        # Get the best match index and score
        best_match_idx = torch.argmax(cos_scores).item()
        occupation_best_score = cos_scores[best_match_idx].item()
        # Get the matched occupation string
        matched_occupation = known_occupations[best_match_idx]
        if occupation_best_score >= 0.7 or fuzzy_score >= 85:
            matched_occupation = matched_occupation if occupation_best_score >= 0.7 else match
            text_to_translate = f"My occupation is {matched_occupation}"
            prompt = f"Give translation of {text_to_translate} in Malay, Thai and Vietnam language without any commentaries"
        else: 
            text_to_translate = f"My Name is {result}"
            prompt = f"Give translation of {text_to_translate} in Malay, Thai and Vietnam language without any commentaries"

    if not text_to_translate:
        return jsonify({"error": "Missing 'text_to_translate' parameter"}), 400
    
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
            "matched_occupation": matched_occupation if (occupation_best_score >= 0.7 or fuzzy_score >= 85) else None,
            "confidence": round(occupation_best_score, 4),
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




