from flask import Flask, render_template, request
from PyPDF2 import PdfReader

app = Flask(__name__)

SKILLS_DB = ["python", "aws", "sql", "docker", "kubernetes"]

def extract_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text.lower()

def analyze(text):
    matched = [s for s in SKILLS_DB if s in text]
    missing = [s for s in SKILLS_DB if s not in text]
    score = int((len(matched) / len(SKILLS_DB)) * 100)
    return score, matched, missing


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['resume']

    if not file:
        return "No file uploaded"

    text = extract_text(file)
    score, matched, missing = analyze(text)

    return render_template(
        "dashboard.html",
        score=score,
        matched_skills=", ".join(matched),
        missing_skills=", ".join(missing),
        suggestions="Improve missing skills and add real projects."
    )

if __name__ == "__main__":
    app.run(debug=True)