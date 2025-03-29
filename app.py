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
            You are a task planner. Break down the task: "{task}" over exactly {days} day(s). The task should be spread out across all {days} days — do not compress or shorten it. Do not return fewer than {days} days.

            Rules:
            - Every 7 days, start a new week. For example:
            - Days 1–7 = Week 1
            - Days 8–14 = Week 2
            - Days 15–21 = Week 3
            - Each week must contain:
            - A title like "Week 1", "Week 2", etc.
            - A short goal summarizing that week's focus
            - Each day must contain:
            - A "date" like "Day 1", "Day 2", ..., up to "Day {days}"
            - A list of subtasks for that day

            Example format:

            {{
            "workflow": [
                {{
                "week": "Week 1",
                "goal": "Your weekly goal",
                "days": [
                    {{
                    "date": "Day 1",
                    "tasks": ["task 1", "task 2"]
                    }}
                ]
                }}
            ]
            }}

            Return valid JSON only, and use all {days} days in your breakdown.
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
        try:
            reply = response.json()['choices'][0]['message']['content']
            print("\n--- RAW AI RESPONSE ---\n", reply, "\n------------------------\n")
            cleaned = reply.strip().replace("```json", "").replace("```", "")
            parsed = json.loads(cleaned)
            return jsonify({
                "raw": reply,
                "workflow": parsed['workflow']
            })
        except Exception as parse_error:
            print("❌ Error parsing AI response:", parse_error)
            print("💬 AI Raw Reply:\n", response.text)
            return jsonify({"error": "Failed to parse AI response"}), 500
        return jsonify(parsed)
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": "Failed to get response from OpenAI"}), 500

if __name__ == '__main__':
    app.run(debug=True)
