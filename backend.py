from flask import Flask, request, jsonify
import requests
from flask_cors import CORS

app = Flask(__name__)

# Only allow requests from localhost:3000
CORS(app, origins=["http://localhost:3000", "https://bim-translator-app-537545827003.asia-southeast1.run.app"])

@app.route('/get_name')
def get_name():
    return "I am the Ann"

@app.route('/translate_string')
def translate_string():
    API_KEY = "sk-hwe6UCi9I0WCUOkekD16oQ"  # Replace with your actual Sea-Lion API key
    SEA_LION_URL = "https://api.sea-lion.ai/v1/chat/completions"
    MODEL_NAME = "aisingapore/Llama-SEA-LION-v3.5-8B-R"
    
    #text_to_translate = request.args.get('text_to_translate')
    text_to_translate = "My Name is Ann"
    
    if not text_to_translate:
        return "Missing 'text_to_translate' parameter", 400
    
    prompt = f"Give translation of {text_to_translate} in Malay, Thai and Vietnam language without any commentaries"
    
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
