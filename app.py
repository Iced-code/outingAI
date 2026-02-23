from flask import Flask, Response, request, render_template, redirect, url_for, jsonify
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional
from google import genai
import os

load_dotenv()
app = Flask(__name__)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

class Activity(BaseModel):
    name: str = Field(description="What the activity is.")
    address: str = Field(description="Address of where the activity will take place.")


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/submit", methods=['POST', 'GET'])
def handle_submit():
    if request.method == 'POST':
        num_persons = request.form.get('num_people')
        date = request.form.get('date')
        earliest_time = request.form.get('earliest-time')
        latest_time = request.form.get('latest-time')
        notes = (request.form.get('notes') or "").strip()
        activity_type = request.form.getlist('activity_type')


        print(f"""
              \ngot num_persons: {num_persons}\ngot date: {date}\ngot earliest time: {earliest_time}
              \ngot latest time: {latest_time}\ngot notes: {notes}\nactivity types: {activity_type}
            """)
        
        output = main({"num_people": num_persons, "date": date, "earliest_time": earliest_time, "latest_time": latest_time, "notes": notes, "activity_type": activity_type})
        
        return jsonify(output)
        # return redirect(url_for('index', ai_output=jsonify(output)))

    return redirect(url_for('index'))

def main(params=None):
    prompt = ""

    if params:
        prompt = f"""
        Create a single plan for an outing for a party of {params["num_people"]}. This outing will take place on {params["date"]} starting
        at {params["earliest_time"]}. It should be at a location within 8 miles of Ashburn, Virginia zipcode 20148. Provide exact locations with addresses. 
        """

        if params["activity_type"]:
            prompt += f"The outing should try to have the following qualities: {params["activity_type"]}. "

        if params["notes"]:
            prompt += f"Keep in mind the following details: {params["notes"]}."

    response = client.models.generate_content(
        model="gemini-2.5-flash", contents= prompt 
    )
    print(response.text)

    return {"message": response.text}

if __name__ == "__main__":
    app.run(debug=True)