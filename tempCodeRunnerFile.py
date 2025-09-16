from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPICallError

api_key = "AIzaSyB9bI9bXvLMyMmWnZy4DKq3-IMTNKUdhwg"
genai.configure(api_key=api_key)

model_name = "gemini-2.5-flash-lite"
model = genai.GenerativeModel(model_name)

chat_sessions = []

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    user_message = request.json.get('message', '').strip()
    if user_message == '':
        return jsonify({"reply": ""})

    try:
        chat_sessions.append({"role": "user", "content": user_message})
        recent_history = chat_sessions[-1:]

        chat = model.start_chat()
        for msg in recent_history:
            chat.send_message(msg["content"])

        response = chat.send_message(user_message)
        bot_reply = response.text.strip().replace('#', '').replace('*', '').replace('جوجل', 'عاصم').replace('Google', 'Aseem')

        chat_sessions.append({"role": "assistant", "content": bot_reply})

        return jsonify({"reply": bot_reply})

    except GoogleAPICallError as e:
        return jsonify({"reply": f"API error: {e}"})
    except Exception as e:
        return jsonify({"reply": f"Unexpected error: {e}"})

if __name__ == "__main__":
    app.run(debug=True)
