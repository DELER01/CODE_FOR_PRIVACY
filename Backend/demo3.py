from flask import Flask, request, jsonify 
from flask_cors import CORS
import os, requests
from flask import render_template
import pdfplumber
from textwrap import wrap
from bs4 import BeautifulSoup
from dotenv import load_dotenv




API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"}
app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index2.html')

@app.route('/receive', methods=['POST'])
def receive_terms():

    text = ""

    # 1. Try to get uploaded file
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '':
            text = extract_text(file)

    # 2. If no file, try textarea input
    if not text:
        text = request.form.get('textarea')
        if not text or text.strip() == "":
            return render_template('index2.html', error="No input provided.")

    # Summarize and show result
    summary = summarize_text(text)
    return render_template('index2.html', summary=summary)
def extract_text(file):
       # Check if the file is a PDF
       if file.filename.endswith('.pdf'):
           with pdfplumber.open(file) as pdf:
               text = ''
               for page in pdf.pages:
                   text += page.extract_text() + '\n'
           return text
       else:
           return file.read().decode('utf-8')  # For text files

def summarize_text(text):
       
       long_text = text


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
