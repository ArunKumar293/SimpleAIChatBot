import os
from dotenv import load_dotenv
from flask import Flask, render_template, request # type: ignore
from openai import AuthenticationError, OpenAI, RateLimitError, api_key

load_dotenv('C:\\Users\\arunk\\OneDrive\\Documents\\GenAI - Scaler\\LLM\\openai_key.env')
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

app = Flask(__name__)

def safe_chat_call(messages):
    """Call OpenAI API with error handling."""
    try:
        return client.chat.completions.create(model="gpt-4o-mini", messages=messages)
    except (AuthenticationError, RateLimitError, Exception):
        return None
    

messages = [
    {
        "role": "system",
        "content": "You are a friendly Python tutor who explains concepts clearly.",
    }
]


@app.route("/", methods=["GET", "POST"])
def index():
    """Handle chat requests."""
    reply = ""
    usage_info = ""

    if request.method == "POST":
        user_text = request.form["user_input"]
        messages.append({"role": "user", "content": user_text})

        resp = safe_chat_call(messages)
        if resp:
            reply = resp.choices[0].message.content
            messages.append({"role": "assistant", "content": reply})
            usage = resp.usage
            usage_info = f"Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}, Total: {usage.total_tokens}"

    return render_template("index.html", reply=reply, usage=usage_info)
