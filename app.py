from flask import Flask, render_template, request
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# =====================================
# AI MODEL
# =====================================
print("Loading AI Model...")
model = SentenceTransformer('all-MiniLM-L6-v2')
print("AI Model Loaded Successfully!")

# =====================================
# JOB DESCRIPTIONS
# =====================================
JOB_DESCRIPTIONS = {
    "Software Engineer": """
    We are looking for a Software Engineer with experience in Python,
    Java, SQL, REST APIs, AWS, Docker, Kubernetes, Git,
    software development lifecycle, debugging, testing,
    problem solving and scalable application development.
    """,

    "Web development": """
    Looking for a Web Developer with knowledge of HTML, CSS,
    JavaScript, React, Node.js, SQL, Git, REST APIs,
    responsive design and frontend/backend development.
    """,

    "Cyber Security Analyst": """
    Knowledge of network security, penetration testing,
    threat detection, SIEM tools, encryption,
    vulnerability assessment and AWS security.
    """,

    "Cloud Engineer": """
    Experience with AWS, Azure, Docker, Kubernetes,
    DevOps, CI/CD pipelines, Terraform,
    cloud infrastructure and monitoring tools.
    """
}

# =====================================
# REQUIRED SKILLS DATABASE
# =====================================
SKILLS_DB = {
    "Software Engineer": [
        "python",
        "java",
        "sql",
        "aws",
        "docker",
        "kubernetes",
        "git",
        "api"
    ],

    "Web development": [
        "html",
        "css",
        "javascript",
        "react",
        "node.js",
        "sql",
        "git",
        "api"
    ],

    "Cyber Security Analyst": [
        "network security",
        "penetration testing",
        "siem",
        "encryption",
        "aws"
    ],

    "Cloud Engineer": [
        "aws",
        "azure",
        "docker",
        "kubernetes",
        "terraform",
        "devops",
        "ci/cd"
    ]
}

# =====================================
# RESUME ANALYSIS FUNCTION
# =====================================
def analyze_resume(resume_text, job_role):

    job_text = JOB_DESCRIPTIONS.get(job_role, "")
    required_skills = SKILLS_DB.get(job_role, [])

    # NLP Semantic Similarity
    embeddings = model.encode([resume_text, job_text])

    semantic_score = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    semantic_score = semantic_score * 100

    # Skill Matching
    matched_skills = []
    missing_skills = []

    for skill in required_skills:
        if skill.lower() in resume_text:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    # Skill Score
    if len(required_skills) > 0:
        skill_score = (
            len(matched_skills) /
            len(required_skills)
        ) * 100
    else:
        skill_score = 0

    # Final ATS Score
    final_score = round(
        (semantic_score * 0.6) +
        (skill_score * 0.4),
        2
    )

    return final_score, matched_skills, missing_skills

# =====================================
# HOME PAGE
# =====================================
@app.route('/')
def home():
    return render_template("index.html")

# =====================================
# UPLOAD AND ANALYZE
# =====================================
@app.route('/upload', methods=['POST'])
def upload():

    file = request.files.get('resume')
    job_role = request.form.get('job_role')

    if not file:
        return "No file uploaded."

    try:

        # Read PDF
        reader = PdfReader(file)

        resume_text = ""

        for page in reader.pages:
            text = page.extract_text()

            if text:
                resume_text += text + " "

        resume_text = resume_text.lower()

        # DEBUGGING
        print("\n========== DEBUG ==========")
        print("Resume Length:", len(resume_text))
        print(resume_text[:1000])
        print("===========================\n")

        # Analyze Resume
        score, matched_skills, missing_skills = analyze_resume(
            resume_text,
            job_role
        )

        # Suggestions
        if score >= 80:
            suggestion = "Excellent match! Your resume aligns well with the selected role."
        elif score >= 60:
            suggestion = "Good match. Add more relevant projects and skills to improve your ATS score."
        else:
            suggestion = "Your resume needs improvement. Consider adding missing skills, certifications, and projects."

        return render_template(
            "dashboard.html",
            score=score,
            matched_skills=", ".join(matched_skills) if matched_skills else "No matching skills found",
            missing_skills=", ".join(missing_skills) if missing_skills else "None",
            suggestions=suggestion
        )

    except Exception as e:
        return f"Error processing resume: {str(e)}"

# =====================================
# RUN APPLICATION
# =====================================
if __name__ == "__main__":
    app.run(debug=True)