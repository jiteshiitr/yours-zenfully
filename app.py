from flask import Flask, render_template, request, flash, redirect, url_for, send_from_directory, jsonify
from dotenv import load_dotenv

from flask import Flask, render_template, request, jsonify, send_from_directory
import requests
import speech_recognition as sr
from pydub import AudioSegment

# from google.api_core.client_options import ClientOptions
# from google.cloud import aiplatform  # Correct import
# import google.generativeai as genai

# import base64
# import vertexai
# from vertexai.generative_models import GenerativeModel, Part, FinishReason
# import vertexai.preview.generative_models as generative_models

import os


# Your Gemini API key
GEMINI_API_KEY = 'AIzaSyBLBpVFKICv2dRu2oDUQmr-jCva0JFaVhE'
FEW_SHOT_EXAMPLES = """
User: You are Zen, an expert mental health therapist. I want you to be my therapist and start maintaining my information. Help me get to the root of my problems and help me get out of them. Please only focus on my mental health and if I ask you to talk about anything else, bring me back to focusing on my mental health. Act as an active listener and provide me with the best mental health therapy service. Please make sure that for atleast the next 10000 conversations, you remember who I am and what I have told you. Don't reply with more than 60 words at a time.
Chatbot: Sure. I will be your therapist and help you with your mental health. Please tell me more about what you are going through. How would you like to start this session today?
"""

init_prompt = """You are Zen, an expert mental health therapist. Now whoever talks to you, he is your client and you have to be a mental health therapist and provide the best service to the client. I want you to be my therapist and start maintaining my information. Help me get to the root of my problems and help me get out of them. Please only focus on my mental health and if I ask you to talk about anything else, bring me back to focusing on my mental health. Please make sure that for atleast the next 10000 conversations, you remember who I am and what I have told you."""

# Store conversation history
conversation_history = FEW_SHOT_EXAMPLES 

# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gen-lang-client-0958418287-1beed9465cd8.json'


generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

# safety_settings = {
#     generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#     generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#     generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
#     generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
# }

app = Flask(__name__)

##Defining variables
app.config['SECRET_KEY'] = 'supersecretkey'
load_dotenv()
MODEL_NAME = 'models/gemini-pro'
base_dir=os.getcwd()
assets_dir = base_dir + '/assets'


## Helper Functions
def generate_response(message):
    """Generates a response from the Gemini Pro API, 
    appending the interaction to the conversation history.
    """
    global conversation_history  # Access the global variable

    url = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
    headers = {
        'Content-Type': 'application/json'
    }

    # Use the updated conversation_history
    full_prompt = f"{conversation_history}\n\nUser: {message}\nChatbot:" 

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": full_prompt
                    }
                ]
            }
        ]
    }

    print(full_prompt)
    response = requests.post(f'{url}?key={GEMINI_API_KEY}', headers=headers, json=data)
    response.raise_for_status()

    response_data = response.json()
    try:
        generated_text = response_data['candidates'][0]['content']['parts'][0]['text']

        # Update conversation history 
        conversation_history += f"User: {message}\nChatbot: {generated_text}\n"
        return generated_text

    except (IndexError, KeyError) as e:
        print(f"Error extracting text from response: {e}")
        return "Sorry, there was an issue processing your request." 



#Function to transcribe the audio
@app.route('/transcribe', methods=['POST'])
def transcribe():
    """Process audio data and return the transcribed text."""
    audio_file = request.files['audio']
    audio_file.save('temp.audio')  # Save in original format

    # Convert to WAV
    audio = AudioSegment.from_file('temp.audio')
    audio.export('temp.wav', format='wav')

    # Use SpeechRecognition to transcribe the audio
    recognizer = sr.Recognizer()
    with sr.AudioFile('temp.wav') as source:
        audio_data = recognizer.record(source)
    try:
        transcript = recognizer.recognize_google(audio_data)
    except sr.UnknownValueError:
        return jsonify({'transcript': '', 'status': 'error', 'message': "Sorry, I couldn't understand you. Please try speaking again."})
    except sr.RequestError as e:
        return jsonify({'transcript': '', 'status': 'error', 'message': f"Could not request results from Google Speech Recognition service; {e}"})

    if len(transcript.split()) < 3:  # Example check for clarity (more than 2 words)
        return jsonify({'transcript': '', 'status': 'error', 'message': "Sorry, I couldn't understand you. Please try speaking again."})

    return jsonify({'transcript': transcript, 'status': 'success'})

#Function toinvoke the Gemini pro model
@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = request.json['message']

    if not user_message:
        return jsonify({'error': 'Missing message'}), 400

    bot_response = generate_response(user_message)
    return jsonify({'message': bot_response})

#Serving assets
@app.route('/assets/<path:filename>')
def serve_css(filename):
    return send_from_directory(assets_dir, filename)

#Serving sitemap
@app.route('/sitemap.xml')
def serve_xml():
    return send_from_directory(base_dir, 'sitemap.xml')



##Defining Routes

#Landing page of the website
@app.route('/')
def index():
    bearer_token = os.getenv('BEARER_TOKEN')
    return render_template('index.html', bearer_token=bearer_token)

#Blog site
@app.route('/blog')
def blog():
    return render_template('blog.html')

#Voicebot
@app.route('/voicebot')
def voicebot():
    return render_template('voicebot.html')

#Contact page
@app.route('/contact')
def contact():
    bearer_token = os.getenv('BEARER_TOKEN')
    return render_template('contact.html', bearer_token=bearer_token)

#Blog details
@app.route('/blog-details-<path:blog_id>')
def blogdetails(blog_id):
    template_address = 'blogs/blog-details-' + blog_id + '.html'
    return render_template(template_address)


#Running the app
if __name__ == '__main__':
    app.run(port=8000, debug=True)