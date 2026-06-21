from flask import Flask, render_template, request
import boto3
from dotenv import load_dotenv
import os
import PyPDF2
import io
from datetime import datetime
from botocore.exceptions import ClientError

load_dotenv()

app = Flask(__name__)

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION")
)

dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="eu-north-1"
)

table = dynamodb.Table('Students')

ses = boto3.client(
    'ses',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name="eu-north-1"
)

SENDER_EMAIL = "avnichandan2465@gmail.com"

BUCKET_NAME = os.getenv("BUCKET_NAME")

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
    all_detected = set()
    for skills in ROLE_SKILLS.values():
        for skill in skills:
            if skill in text:
                all_detected.add(skill)

    role_skills = ROLE_SKILLS.get(selected_role, [])
    matched = [s for s in role_skills if s in text]
    missing = [s for s in role_skills if s not in text]

    score = int((len(matched) / len(role_skills)) * 100) if role_skills else 0

    role_scores = {}
    for role, skills in ROLE_SKILLS.items():
        matched_count = sum(1 for s in skills if s in text)
        role_scores[role] = int((matched_count / len(skills)) * 100)

    best_role = max(role_scores, key=role_scores.get)

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

def send_email_report(to_email, name, results):
    subject = "📊 Your Resume Analysis Report - Smart Placement Analyzer"

    body_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 600px; margin: auto; background: white; border-radius: 10px; padding: 30px;">
            <h2 style="color: #4f46e5;">📄 Resume Analysis Report</h2>
            <p>Hi <strong>{name}</strong>,</p>
            <p>Here's your resume analysis summary:</p>

            <div style="background: #f0f0ff; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h3 style="color: #7c3aed; margin: 0;">🎯 ATS Score: {results['score']}%</h3>
            </div>

            <p><strong>✅ Matched Skills:</strong><br>{results['matched_skills']}</p>
            <p><strong>❌ Missing Skills:</strong><br>{results['missing_skills']}</p>
            <p><strong>🏆 Best Fit Role:</strong> {results['best_role']}</p>
            <p><strong>💡 Recommendation:</strong><br>{results['suggestions']}</p>

            <hr style="margin: 20px 0;">
            <p style="color: #888; font-size: 0.9em;">Sent automatically by Smart Placement Analyzer 🚀</p>
        </div>
    </body>
    </html>
    """

    try:
        ses.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': body_html}}
            }
        )
        print(f"✅ Email sent to {to_email}")
    except ClientError as e:
        print(f"❌ SES Error: {e.response['Error']['Message']}")


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
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    job_role = request.form.get('job_role', 'Software Engineer')
    file = request.files['resume']

    if file:
        file_bytes = file.read()

        # Upload to S3
        s3.upload_fileobj(
            io.BytesIO(file_bytes),
            BUCKET_NAME,
            file.filename
        )

        # Analyze resume
        text = extract_text_from_pdf(file_bytes)
        results = analyze_resume(text, job_role)

        # Save to DynamoDB
        try:
            table.put_item(Item={
                'email': email,
                'name': name,
                'job_role': job_role,
                'filename': file.filename,
                'ats_score': results['score'],
                'matched_skills': results['matched_skills'],
                'missing_skills': results['missing_skills'],
                'best_role': results['best_role'],
                'uploaded_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            print(f"✅ Saved to DynamoDB: {email}")
        except Exception as e:
            print(f"❌ DynamoDB Error: {e}")

            # Send email report
        send_email_report(email, name, results)

        return render_template('dashboard.html',
            name=name,
            email=email,
            job_role=job_role,
            **results
        )

    return "No file selected"


if __name__ == '__main__':
    app.run(debug=True)