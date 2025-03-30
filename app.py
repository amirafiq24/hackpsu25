from flask import Flask, request, jsonify
from flask_cors import CORS

import requests
import json

app = Flask(__name__)
CORS(app)

import os
from dotenv import load_dotenv
load_dotenv()  # ⬅️ Load environment variables from .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    data = request.get_json()
    task = data.get('task')
    days = data.get('days')

    prompt = f"""
You are a task planner. Break down the task: "{task}" into a plan of less than or equal {days} day(s). Do not exceed {days} days in total.

Instructions:
- Do NOT use "Week 1", "Week 2", etc.
- If it is possible to complete the task in less than {days} days, do so.
- Make tasks smaller and more manageable.
- There should be only one goal per day
- Give more detailed tasks descriptions.
- Next to task, include suggested time to complete it in minutes or hours.
- Add additional notes if necessary.
- Instead, group the breakdown by **goal or phase of work**.
- Each goal block should include:
  - A clear "goal" title
  - A list of days with specific tasks
- Start a new goal block **only** when the focus or phase of the work changes.


Each day should include:
- A label like "Day 1", "Day 2", ..., up to "Day {days}"
- A list of clear, actionable tasks for that day

Format your response like this (valid JSON):

{{
  "workflow": [
    {{
      "goal": "First goal or phase",
      "days": [
        {{
          "date": "Day 1",
          "tasks": ["task 1", "task 2"]
        }},
        ...
      ]
    }},
    {{
      "goal": "Next goal or phase",
      "days": [
        {{
          "date": "Day 4",
          "tasks": ["task 1"]
        }}
      ]
    }}
  ]
}}

"""


    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        reply = response.json()['choices'][0]['message']['content']
        cleaned = reply.strip().replace("```json", "").replace("```", "")
        parsed = json.loads(cleaned)

        return jsonify({
            "workflow": parsed['workflow'],
        })
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Failed to get response from OpenAI"}), 500

@app.route('/explain-task', methods=['POST'])
def explain_task():
    data = request.get_json()
    task = data.get('task')

    prompt = f"""
You are an assistant helping users understand to-do list tasks.

For the task: "{task}", return a JSON object with this structure:

{{
  "what": "...",        # What the task means
  "why": "...",         # Why it's important
  "tips": "..."         # Helpful tips to complete it
}}
For what it means, don't just repeat the task. Explain it in a way that someone who doesn't know what it is would understand.
Be concise and clear. Return only the JSON object.
"""

    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.5
    }

    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        reply = response.json()['choices'][0]['message']['content']
        cleaned = reply.strip().replace("```json", "").replace("```", "")
        parsed = json.loads(cleaned)
        return jsonify(parsed)

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Failed to fetch explanation"}), 500

if __name__ == '__main__':
    app.run(debug=True)
