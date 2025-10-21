from flask import Blueprint, render_template, request
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a Blueprint
interview_assistant_bp = Blueprint(
    'interview_assistant_bp',
    __name__,
    url_prefix='/projects/interview-assistant-app',
    template_folder='templates'
)

# Load OpenAI API key from env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@interview_assistant_bp.route("/", methods=["GET", "POST"])
def interview_assistant():
    result = ""

    if request.method == "POST":
        behaviour = request.form.get("behaviour")
        scenario = request.form.get("scenario")
        experience = request.form.get("experience")

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a helpful assistant for UK Civil Service job preparation.\n"
                            "Always answer using the STAR method:\n"
                            "- Situation: Describe the background and context.\n"
                            "- Task: Outline what needed to be done.\n"
                            "- Action: Explain what *you* specifically did.\n"
                            "- Result: Describe the outcome and any impact."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"You are an expert in Civil Service recruitment.\n"
                            f"Write a STAR-format response for a UK Civil Service interview.\n\n"
                            f"Behaviour: {behaviour}\n"
                            f"Scenario: {scenario}\n"
                            f"Experience: {experience}\n\n"
                            "Use a professional but conversational tone. Make the response realistic and well-structured.\n"
                            "Output only the STAR response."
                        )
                    }
                ]
            )
            result = response.choices[0].message.content.strip()
        except Exception as e:
            result = f"Error: {e}"

    return render_template("assistant.html", result=result)