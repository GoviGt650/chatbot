from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os

# Load Gemini API Key from environment
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Define Gemini model with domain-restricted system prompt
model = genai.GenerativeModel(
    model_name="gemini-pro",
    system_instruction="""
You are a healthcare assistant AI. Your job is to assist users with only healthcare-related questions like symptoms, diseases, medications (informational only), diet, fitness, mental health, and first-aid.

If the user asks anything unrelated to healthcare (like politics, tech, celebrities, general knowledge), kindly respond with:
"I'm sorry, but I can only help with healthcare-related queries."

Never respond to questions outside the healthcare domain.
"""
)

# Start a chat session
chat = model.start_chat(history=[])

app = Flask(__name__)

# Keyword filter to ensure queries are related to healthcare
def is_healthcare_related(query):
    keywords = [
        'symptom', 'medicine', 'disease', 'doctor', 'hospital',
        'treatment', 'pain', 'injury', 'health', 'mental', 'diabetes',
        'blood pressure', 'covid', 'infection', 'fever', 'fitness', 'diet'
    ]
    return any(word in query.lower() for word in keywords)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat_response():
    user_input = request.json.get('message')

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    if not is_healthcare_related(user_input):
        return jsonify({
            "response": "I'm sorry, but I can only help with healthcare-related queries."
        })

    try:
        response = chat.send_message(user_input)
        return jsonify({"response": response.text})
    except Exception as e:
        # 🔥 Print the actual Gemini API error for debugging (shows up in Render logs)
        print("❌ Gemini API Error:", e)
        return jsonify({
            "response": "Sorry, there was an error processing your request."
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Required for Render
    app.run(host='0.0.0.0', port=port)
