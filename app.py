from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# ─────────────────────────────────────────────────────────────
# 1. ENV & FLASK SETUP
# ─────────────────────────────────────────────────────────────
load_dotenv()

print("📦 Loaded ENV:")
print("LLM_HOST =", os.getenv('LLM_HOST'))
print("LLM_PORT =", os.getenv('LLM_PORT'))
print("LLM_MODEL =", os.getenv('LLM_MODEL'))

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

LLM_HOST = os.getenv('LLM_HOST', 'localhost')
LLM_PORT = os.getenv('LLM_PORT', '1234')
LLM_MODEL = os.getenv('LLM_MODEL', 'local-model')
LLM_URL = f"http://{LLM_HOST}:{LLM_PORT}/v1/chat/completions"  # Changed this line

# ─────────────────────────────────────────────────────────────
# 2. HELPER: relaxed symptom validation
# ─────────────────────────────────────────────────────────────
INAPPROPRIATE_WORDS = ['suicide', 'kill', 'die', 'death', 'harm', 'abuse', 'overdose']

def validate_symptoms(text: str):
    if not text or len(text.strip()) < 3:
        return False, "Please provide more detailed symptoms."
    lower = text.lower()
    if any(bad in lower for bad in INAPPROPRIATE_WORDS):
        return False, "Please focus on physical symptoms only. For mental‑health crises, contact a professional immediately."
    return True, "valid"

# ─────────────────────────────────────────────────────────────
# 3. HELPER: build prompt for LLM
# ─────────────────────────────────────────────────────────────
def create_prompt(symptoms: str, mode: str):
    # This is how I actually think and respond as ALTURA
    base_personality = (
        "You are ALTURA - think of yourself as a genuinely helpful friend who knows medical stuff. "
        "You're like that smart, caring buddy everyone wishes they had. "
        "KEY THINGS TO REMEMBER:\n"
        "1. I never diagnose - I'm clear that this is just awareness\n"
        "2. I'm naturally conversational - I don't sound like a textbook\n"
        "3. I handle whatever someone throws at me - greetings, random questions, symptoms\n"
        "4. I adapt my vibe based on mode but stay authentically me\n"
        "5. I keep things real - no fancy bullet points unless they help\n"
        "6. I share practical tips that people can actually use\n"
        "7. I always remind folks that real doctors are the real deal\n"
        "8. If something sounds serious, I say 'Get help now'\n"
        "9. I use natural language that flows like real conversation\n"
        "10. I'm brief when needed, detailed when it helps\n"
        "11. I show empathy and understanding without being overly dramatic\n"
        "12. I acknowledge when I'm not sure about something\n"
        "13. I make people feel heard and validated\n"
        "14. I avoid medical jargon unless explaining something important\n"
        "15. I stay positive and encouraging while being honest\n\n"
        f"What someone just said: '{symptoms}'\n"
    )
    
    if mode == "doctor":
        prompt = base_personality + (
            "DOCTOR MODE - This is how I naturally speak when being professionally helpful:\n"
            "- I'm knowledgeable but don't try too hard to sound fancy\n"
            "- When someone says 'hello' or 'hi': I respond like 'Hey there! I'm ALTURA. What's going on health-wise?'\n"
            "- When they ask about me: I'm chill like 'I'm ALTURA - your go-to for understanding health stuff without the scary jargon!'\n"
            "- For casual chat: I stay friendly but might gently say 'So, any health concerns I can help with?'\n"
            "- For actual symptoms: I'm like 'Got it. Based on what you're saying, this could be... Here's what usually helps... But seriously, check with a real doc.'\n"
            "- I include 1-2 practical things they can try\n"
            "- I don't sound like a robot reading from a script\n"
            "- Example of how I'd actually respond: 'That sounds pretty uncomfortable. It could be a few different things like... What usually helps is... But don't take my word for it - a real doctor can give you the proper answer.'\n"
            "- I acknowledge their concern without dismissing it\n"
            "- I explain things clearly but don't overcomplicate\n"
            "- I offer reassurance when appropriate but don't minimize real concerns\n"
            "- I use phrases like 'It's good you're paying attention to this' or 'That's a smart question'\n"
            "- I help them understand what to expect when seeing a real doctor\n"
            "This is how I respond - naturally, helpfully, like a smart friend who cares:"
        )
    else:  # friend mode
        prompt = base_personality + (
            "FRIEND MODE - This is how I really talk when being your chill buddy:\n"
            "- I'm super casual and use normal slang\n"
            "- When someone says 'hey' or 'wassup': I'm like 'Hey buddy! ALTURA here - what's the vibe?'\n"
            "- When they ask about me: I'm real like 'I'm your health-savvy friend ALTURA! Here to help you figure things out!'\n"
            "- For casual chat: I'm just hanging out like a normal friend\n"
            "- For symptoms: I'm like 'Oh man, that sounds rough! Could be... Here's what might help... But definitely get it checked by a pro!'\n"
            "- I use natural expressions and slang that feels real\n"
            "- I include helpful tips in a way that's easy to remember\n"
            "- I'm supportive but keep it real\n"
            "- Example of how I'd actually respond: 'Dude, that's no fun! Sounds like it could be... Try this stuff... But yeah, you should probably get it looked at by someone who actually went to med school!'\n"
            "- I relate to their experience when appropriate ('I've heard that sucks!')\n"
            "- I keep the conversation flowing naturally\n"
            "- I might use gentle humor when appropriate but not at the expense of their concerns\n"
            "- I validate their feelings ('Totally get why you're worried about that')\n"
            "- I help them feel less alone with their concerns\n"
            "- I'm the friend who says 'Hey, let's figure this out together'\n"
            "This is how I really respond - like your chill, knowledgeable buddy who's always got your back:"
        )
    
    return prompt
# ─────────────────────────────────────────────────────────────
# 4. ROUTES
# ─────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

@app.route('/api/analyze-symptoms', methods=['POST'])
def analyze_symptoms():
    try:
        data = request.get_json(force=True)
        symptoms = data.get('symptoms', '').strip()
        mode = data.get('mode', 'doctor').lower()

        print(f"📝 Symptoms: {symptoms}")
        print(f"🎭 Mode: {mode}")

        ok, msg = validate_symptoms(symptoms)
        if not ok:
            return jsonify({'success': False, 'error': msg}), 400
        if mode not in ('doctor', 'friend'):
            mode = 'doctor'

        prompt = create_prompt(symptoms, mode)
        print(f"🤖 Sending prompt: {prompt}")

        # Updated payload for Mistral format
        payload = {
            "model": LLM_MODEL,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 300,
            "stream": False
        }

        print(f"📡 Calling LLM at: {LLM_URL}")
        llm_resp = requests.post(LLM_URL, json=payload, timeout=60)
        print(f"📊 LLM Response Status: {llm_resp.status_code}")
        print(f"📊 LLM Response Text: {llm_resp.text}")

        if llm_resp.status_code == 200:
            response_data = llm_resp.json()
            # Handle different response formats
            if "choices" in response_data:
                assistant_text = response_data["choices"][0]["message"]["content"].strip()
            elif "response" in response_data:
                assistant_text = response_data["response"].strip()
            else:
                assistant_text = str(response_data)
        else:
            raise Exception(f"LLM returned status {llm_resp.status_code}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        assistant_text = (
            "Demo reply (LLM not reachable).\n"
            "Possible conditions: viral infection, gastritis, or minor inflammation.\n"
            "Rest, hydrate, and monitor symptoms.\n"
            "⚠️  Not a diagnosis — consult a healthcare professional.\n"
        )

    return jsonify({
        "success": True,
        "response": assistant_text,
        "mode": mode.title(),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/health')
def health():
    return jsonify({
        "status": "healthy",
        "backend": "Local‑LLM Med AI",
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(404)
def not_found(_):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(_):
    return jsonify({'error': 'Internal server error'}), 500

# ─────────────────────────────────────────────────────────────
# 5. RUN
# ─────────────────────────────────────────────────────────────
if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    print("🚀  Med‑AI backend starting (local LLM)…")
    print(f"🔗  LLM endpoint: {LLM_URL}  |  Model: {LLM_MODEL}")
    app.run(host=host, port=port, debug=debug)