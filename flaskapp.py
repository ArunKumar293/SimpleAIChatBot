import base64
import os
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, url_for # type: ignore
from openai import AuthenticationError, OpenAI, RateLimitError, api_key

load_dotenv('C:\\Users\\arunk\\OneDrive\\Documents\\GenAI - Scaler\\LLM\\openai_key.env')
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

app = Flask(__name__)

SYSTEM_PROMPT = "You are a friendly assistant who does its best to help!"

# Track conversation via previous_response_id (reset on server restart)
last_response_id = None


def safe_responses_call(user_input, previous_response_id=None):
    try:
        return client.responses.create(
            model="gpt-5-nano",
            instructions=SYSTEM_PROMPT,
            input=user_input,
            previous_response_id=previous_response_id,
        )
    except (AuthenticationError, RateLimitError, Exception) as e:
        print(f"API Error: {e}")
        return None


@app.route("/", methods=["GET", "POST"])
def index():
    """Handle chat requests."""
    global last_response_id
    reply = ""
    usage_info = ""

    if request.method == "POST":
        user_text = request.form.get("user_input", "")
        image_file = request.files.get("image")
       
        content = []
        
        if user_text:
            content.append(
                {"type": "input_text", 
                 "text": user_text
                 }
            )
            
        if image_file and image_file.filename:
            img_b64 = base64.b64encode(image_file.read()).decode("utf-8")
            mime = image_file.content_type or "image/png"
            content.append(
                {"type": "input_image", 
                 "image_url": f"data:{mime};base64,{img_b64}",
                }
            )    

        if content:
            user_msg = [{"role": "user", "content": content}]
            resp = safe_responses_call(user_msg, last_response_id)
            if resp:
                last_response_id = resp.id
                reply = resp.output_text
                usage = resp.usage
                usage_info = ( 
                    f"Input: {usage.input_tokens}, " 
                    f"Output: {usage.output_tokens}, " 
                    f"Total: {usage.total_tokens}"
                )

    return render_template("index.html", reply=reply, usage=usage_info)


@app.route("/reset", methods=["GET", "POST"])
def reset():
    """Reset conversation context."""
    global last_response_id
    last_response_id = None
    return redirect(url_for("index"))