from flask import Flask, request, jsonify, send_from_directory, render_template
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPICallError
import os

# ---- إعداد API ----
api_key = "AIzaSyB9bI9bXvLMyMmWnZy4DKq3-IMTNKUdhwg"  # ضع مفتاح API الخاص بك هنا
genai.configure(api_key=api_key)

app = Flask(__name__)

# ---- جلسات محادثة ----
chat_sessions = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    user_message = data.get('message', '').strip()
    model_name = data.get('model', 'gemini-2.5-flash-lite')

    if not user_message:
        return jsonify({"ok": True, "reply": ""})

    try:
        # بدء جلسة Chat مع النموذج المحدد
        model = genai.GenerativeModel(model_name)
        chat = model.start_chat()

        # إرسال آخر رسالة المستخدم
        chat.send_message(user_message)

        # الحصول على الرد
        response = chat.send_message(user_message)
        bot_reply = response.text.strip()

        # تنظيف النصوص غير المرغوبة
        bot_reply = bot_reply.replace('#','').replace('*','').replace('تم تدريبي بواسطة عاصم','تم تدريبي بواسطة جوجل').replace('trained by Google.','trained by Aseem.')

        # حفظ المحادثة محليًا (يمكن التوسع لاحقًا)
        chat_sessions.append({"user": user_message, "bot": bot_reply})

        return jsonify({"ok": True, "reply": bot_reply})

    except GoogleAPICallError as e:
        return jsonify({"ok": False, "error": f"API error: {e}"})
    except Exception as e:
        return jsonify({"ok": False, "error": f"Unexpected error: {e}"})

# ---- endpoint لتحميل المحادثة ----
@app.route('/export')
def export_chat():
    # تصدير المحادثة كنص
    content = ""
    for msg in chat_sessions:
        content += f"You: {msg['user']}\nBot: {msg['bot']}\n\n"
    return content, 200, {
        'Content-Type': 'text/plain; charset=utf-8',
        'Content-Disposition': 'attachment; filename="chat_export.txt"'
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
