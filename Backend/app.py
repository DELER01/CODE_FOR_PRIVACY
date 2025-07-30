from flask import Flask, request, jsonify
from flask_cors import CORS
from textwrap import wrap
from dotenv import load_dotenv
import os, requests
from flask import render_template



load_dotenv()




API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"}

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return "Server is running!"

@app.route('/receive', methods=['POST'])
def receive_terms():
    data = request.get_json()
    terms = data.get('terms')

    if not terms:
        return jsonify({"status": "error", "message": "No terms received"}), 400

    # Save full content to a file
    with open("terms_and_conditions.txt", "w", encoding="utf-8") as file:
        file.write(terms)

    print("✔ Terms successfully written to file.")
    


    summary = summarize_text(terms)
    summary2 = summarize_text(summary)
    summary3 = summarize_text(summary2)

    return jsonify({"summary":summary})

def summarize_text(terms):
       
       long_text = terms


       chunks = wrap(long_text, 1000)

       summaries = []

       for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        response = requests.post(API_URL, headers=headers, json={"inputs": chunk})

        if response.status_code == 200:
          summary = response.json()[0]["summary_text"]
          summaries.append(summary)
        else:
          print(f"❌ Chunk {i+1} failed with status {response.status_code}")
          print(response.text)

# Combine summaries
       final_summary = "\n".join(summaries)
       print("\n✅ Final Combined Summary:\n", final_summary)
       return final_summary


if __name__ == '__main__':
    app.run(debug=True)
