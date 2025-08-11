from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)

# Only allow requests from localhost:3000
CORS(app, origins=["http://localhost:3000"])

@app.route('/get_name')
def get_name():
    return "I am the Ann"

@app.route('/translate_string')
def translate_string():
    text_to_translate = request.args.get('text_to_translate')
    
    if not text_to_translate:
        return "Missing 'text_to_translate' parameter", 400

    return "私の名前はあんちゃんです"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
