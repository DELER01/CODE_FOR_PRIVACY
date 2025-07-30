from flask import Flask, request, render_template
from flask_cors import CORS
import os, requests
import pdfplumber
from bs4 import BeautifulSoup
from textwrap import wrap
from dotenv import load_dotenv

load_dotenv()

API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {os.getenv('HF_API_KEY')}"}

app = Flask(__name__, template_folder="templates")
CORS(app)

@app.route('/', methods=['GET'])
def home():
    return render_template('index3.html')

@app.route("/receive", methods=["POST"])
def receive_terms():
    text = ""

    # From uploaded file
    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '':
            text = extract_text(file)

    # From textarea
    if not text:
        textarea_input = request.form.get("textarea")
        if textarea_input and textarea_input.strip() != "":
            text = textarea_input.strip()

    # From URL
    if not text:
        url = request.form.get("url")
        if url and url.strip() != "":
            text = extract_text_from_url(url.strip())
            if not text:
                return render_template("index3.html", error="❌ Could not extract content from URL.")

    if not text:
        return render_template("index3.html", error="❌ No input provided.")

    summary = summarize_text(text)
    return render_template("index3.html", summary=summary)

def extract_text(file):
    if file.filename.endswith('.pdf'):
        try:
            with pdfplumber.open(file) as pdf:
                return "\n".join(page.extract_text() or '' for page in pdf.pages)
        except Exception as e:
            print("PDF extraction error:", e)
            return ""
    else:
        return file.read().decode('utf-8')

def extract_text_from_url(url):
    try:
        response = requests.get(url, timeout=5)
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        return ' '.join(soup.stripped_strings)
    except Exception as e:
        print("URL extraction error:", e)
        return ""

def summarize_text(text):
    chunks = wrap(text, 700)  # reduce chunk size for memory
    summaries = []
    for i, chunk in enumerate(chunks):
        try:
            print(f"🔄 Processing chunk {i+1}/{len(chunks)}...")
            response = requests.post(API_URL, headers=headers, json={"inputs": chunk})
            if response.status_code == 200:
                summaries.append(response.json()[0]["summary_text"])
            else:
                print(f"❌ Failed: Chunk {i+1} - {response.status_code}")
        except Exception as e:
            print(f"❌ Exception on chunk {i+1}: {e}")
    return "\n".join(summaries) if summaries else "❌ Summarization failed."

if __name__ == '__main__':
    app.run(debug=True)
