from flask import Flask, render_template, request
import boto3
from dotenv import load_dotenv
import os
import PyPDF2
import io

load_dotenv()

app = Flask(__name__)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

BUCKET_NAME = os.getenv("BUCKET_NAME")

# Skills database for each role
ROLE_SKILLS = {
    "Software Engineer": ["python", "java", "c++", "data structures", "algorithms", "git", "sql", "linux", "oop", "rest api"],
    "Web Development": ["html", "css", "javascript", "react", "nodejs", "git", "sql", "rest api", "bootstrap", "mongodb"],
    "Cyber Security Analyst": ["networking", "linux", "firewalls", "siem", "python", "ethical hacking", "nmap", "wireshark", "encryption", "risk assessment"],
    "Cloud Engineer": ["aws", "azure", "gcp", "docker", "kubernetes", "terraform", "linux", "networking", "python", "ci/cd"]
}


def extract_text_from_pdf(file_bytes):
    reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text.lower()


def analyze_resume(text, selected_role):
    # Detect all skills from resume across all roles
    all_detected = set()
    for skills in ROLE_SKILLS.values():
        for skill in skills:
            if skill in text:
                all_detected.add(skill)

    # Match against selected role
    role_skills = ROLE_SKILLS.get(selected_role, [])
    matched = [s for s in role_skills if s in text]
    missing = [s for s in role_skills if s not in text]

    # ATS score based on selected role
    score = int((len(matched) / len(role_skills)) * 100) if role_skills else 0

    # Role comparison scores
    role_scores = {}
    for role, skills in ROLE_SKILLS.items():
        matched_count = sum(1 for s in skills if s in text)
        role_scores[role] = int((matched_count / len(skills)) * 100)

    # Best fit role
    best_role = max(role_scores, key=role_scores.get)

    # Suggestions
    if missing:
        suggestions = f"Consider adding these skills to improve your resume: {', '.join(missing)}"
    else:
        suggestions = "Great! Your resume matches all key skills for this role."

    return {
        "score": score,
        "all_skills": ", ".join(all_detected) if all_detected else "No known skills detected",
        "matched_skills": ", ".join(matched) if matched else "None",
        "missing_skills": ", ".join(missing) if missing else "None",
        "best_role": best_role,
        "role_scores": role_scores,
        "suggestions": suggestions
    }


@app.route('/')
def home():
    objects = s3.list_objects_v2(Bucket=BUCKET_NAME)
    files = []
    if 'Contents' in objects:
        for obj in objects['Contents']:
            files.append(obj['Key'])
    return render_template('index.html', files=files)


@app.route('/upload', methods=['POST'])
def upload():
    job_role = request.form.get('job_role', 'Software Engineer')
    print("Selected role:", job_role)
    file = request.files['resume']

    if file:
        # Read file bytes
        file_bytes = file.read()

        # Upload to S3
        s3.upload_fileobj(
            io.BytesIO(file_bytes),
            BUCKET_NAME,
            file.filename
        )

        # Extract text and analyze
        text = extract_text_from_pdf(file_bytes)
        results = analyze_resume(text, job_role)

        # Render dashboard with results
        return render_template('dashboard.html', **results)

    return "No file selected"


if __name__ == '__main__':
    app.run(debug=True)