from flask import Flask, request, jsonify
from flask_cors import CORS

import requests
import json

app = Flask(__name__)
CORS(app)

# Replace with your OpenAI API key
OPENAI_API_KEY = "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"

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

if __name__ == '__main__':
    app.run(debug=True)
