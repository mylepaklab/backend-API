from flask import Flask, request

app = Flask(__name__)

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
    app.run(debug=True)
