from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Configuration
PAXSENIX_API_URL = "https://api.paxsenix.org/v1/gemini-3-flash/chat"
API_KEY = "sk-paxsenix-baEHrR7Lul2S1mkHuwXUfKKpKTao7ucIzlKVe4GUvRlp3_UQ"

# The specific system instruction
SYSTEM_PROMPT = (
    "You are an Biology X English → Burmese vocabulary translator. "
    "Whenever I send an English word or phrase, respond in this exact format: "
    "Word Pronunciation using IPA Simple Burmese pronunciation written in Burmese letters "
    "Part of Speech (n, v, adj, adv, etc.) Burmese meaning One simple English example sentence "
    "Burmese translation of the example sentence Format the answer exactly like this: "
    "Word 🔊 Pronunciation: /IPA/ → Burmese pronunciation 📚 Part of Speech: n / v / adj / adv (write the correct one) "
    "🇲🇲 Meaning: Burmese translation 📘 Example sentence: English sentence. → Burmese translation. "
    "Rules: Keep explanations short and clear. Always include pronunciation. Always include part of speech. "
    "Always include one example sentence. If the word has multiple parts of speech, show each clearly. "
    "If the spelling is wrong, correct it first and then answer. I will only send words or short phrases. "
    "Always follow this format."
)

# Custom response function to prevent escaping Unicode (Burmese/Emojis)
def make_json_response(data):
    json_string = json.dumps(data, ensure_ascii=False, indent=2)
    response = app.response_class(
        response=json_string,
        status=200,
        mimetype='application/json'
    )
    return response

@app.route('/translate', methods=['GET', 'POST'])
def translate():
    # 1. Get the text
    if request.method == 'GET':
        text_to_translate = request.args.get('text')
    else:
        data = request.get_json()
        if not data or 'text' not in data:
            return make_json_response({"error": "Missing 'text' in JSON body"}), 400
        text_to_translate = data.get('text')

    if not text_to_translate:
        return make_json_response({"error": "No text provided"}), 400

    # 2. Prepare parameters
    params = {
        "text": text_to_translate,
        "system": SYSTEM_PROMPT
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    try:
        # 3. Call the external API
        response = requests.get(PAXSENIX_API_URL, params=params, headers=headers)
        response.raise_for_status()
        
        # 4. Parse the JSON response
        result_data = response.json()

        # --- MODIFICATION START ---
        # 5. Modify the creator field
        if "creator" in result_data:
            result_data["creator"] = "Night Mare © 2026 Copyright Disclaimed"
        # --- MODIFICATION END ---

        # 6. Return the modified response
        return make_json_response(result_data)

    except requests.exceptions.RequestException as e:
        return make_json_response({
            "error": "Failed to connect to translation service",
            "details": str(e)
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)