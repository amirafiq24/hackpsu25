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

    prompt = f'''You are a task planner. Break down the task: "{task}" over {days} days into a structured weekly plan. Each week should have a title and a goal. Each day should have a date label and a list of subtasks. Format your response as structured JSON like this:

{{
  "workflow": [
    {{
      "week": "Week 1 (March 31 - April 4)",
      "goal": "Your weekly goal here",
      "days": [
        {{
          "date": "March 31 (Mon)",
          "tasks": ["task 1", "task 2"]
        }}
      ]
    }}
  ]
}}'''

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
