from flask import Flask, request, jsonify 
from flask_cors import CORS
import os, requests
from flask import render_template
import pdfplumber
from textwrap import wrap
from bs4 import BeautifulSoup
from dotenv import load_dotenv



load_dotenv()




API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"}

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index3.html')


@app.route("/receive", methods=["POST"])
def receive_terms():
    text = ""

    # 1. Try file input
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '':
            text = extract_text(file)

    # 2. Try textarea
    if not text:
        textarea_input = request.form.get("textarea")
        if textarea_input and textarea_input.strip() != "":
            text = textarea_input.strip()

    # 3. Try URL
    if not text:
        url = request.form.get("url")
        if url and url.strip() != "":
            text = extract_text_from_url(url.strip())
            if not text:
                return render_template("index3.html", error="Could not extract content from URL.")

    if not text:
        return render_template("index3.html", error="No input provided.")

    summary = summarize_text(text)
    summary2 = summarize_text(summary)
    summary3 = summarize_text(summary2)

    return render_template("index3.html", summary=summary3)


def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove scripts, styles, and navs for cleaner content
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()

        # Join all visible text
        text = ' '.join(soup.stripped_strings)
        return text
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return ""
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
