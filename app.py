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
# SKILL ALIASES
# =====================================
SKILL_ALIASES = {
    "python": ["python"],
    "java": ["java"],
    "sql": ["sql"],

    "html": ["html"],
    "css": ["css"],

    "javascript": [
        "javascript",
        "js"
    ],

    "react": [
        "react",
        "reactjs",
        "react js",
        "react.js"
    ],

    "node.js": [
        "node",
        "nodejs",
        "node js",
        "node.js"
    ],

    "git": ["git"],

    "aws": [
        "aws",
        "amazon web services"
    ],

    "docker": ["docker"],

    "kubernetes": [
        "kubernetes",
        "k8s"
    ],

    "api": [
        "api",
        "rest api",
        "restful api"
    ],

    "penetration testing": [
        "penetration testing",
        "pentesting"
    ],

    "network security": [
        "network security"
    ],

    "siem": [
        "siem"
    ],

    "encryption": [
        "encryption"
    ],

    "azure": [
        "azure"
    ],

    "terraform": [
        "terraform"
    ],

    "devops": [
        "devops"
    ],

    "ci/cd": [
        "ci/cd",
        "cicd"
    ]
}

# =====================================
# ROLE-SPECIFIC REQUIRED SKILLS
# =====================================
ROLE_SKILLS = {
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
        "git"
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
# FIND SKILLS IN RESUME
# =====================================
def find_skills(resume_text, required_skills):

    matched_skills = []
    missing_skills = []

    for skill in required_skills:

        aliases = SKILL_ALIASES.get(skill, [skill])

        found = False

        for alias in aliases:
            if alias.lower() in resume_text:
                found = True
                break

        if found:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    return matched_skills, missing_skills

def extract_all_skills(resume_text):

    found_skills = []

    for skill, aliases in SKILL_ALIASES.items():

        for alias in aliases:

            if alias.lower() in resume_text:

                if skill not in found_skills:
                    found_skills.append(skill)

                break

    return found_skills


# =====================================
# ANALYZE RESUME
# =====================================
def analyze_resume(resume_text, job_role):

    job_text = JOB_DESCRIPTIONS.get(job_role, "")

    embeddings = model.encode(
        [resume_text, job_text]
    )

    semantic_score = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]]
    )[0][0]

    semantic_score = semantic_score * 100

    required_skills = ROLE_SKILLS.get(job_role, [])

    matched_skills, missing_skills = find_skills(
        resume_text,
        required_skills
    )

    if len(required_skills) > 0:
        skill_score = (
            len(matched_skills) /
            len(required_skills)
        ) * 100
    else:
        skill_score = 0

    final_score = round(
        (semantic_score * 0.6) +
        (skill_score * 0.4),
        2
    )

    return final_score, matched_skills, missing_skills

def compare_all_roles(resume_text):

    role_scores = {}

    for role in JOB_DESCRIPTIONS.keys():

        score, _, _ = analyze_resume(
            resume_text,
            role
        )

        role_scores[role] = score

    best_role = max(
        role_scores,
        key=role_scores.get
    )

    return role_scores, best_role


# =====================================
# HOME PAGE
# =====================================
@app.route('/')
def home():
    return render_template("index.html")


# =====================================
# UPLOAD PAGE
# =====================================
@app.route('/upload', methods=['POST'])
def upload():

    file = request.files.get('resume')
    job_role = request.form.get('job_role')

    if not file:
        return "No file uploaded."

    try:

        reader = PdfReader(file)

        resume_text = ""

        for page in reader.pages:

            text = page.extract_text()

            if text:
                resume_text += text + " "

        resume_text = resume_text.lower()

        # =================================
        # DEBUG OUTPUT
        # =================================
        print("\n======= RESUME TEXT =======\n")
        print(resume_text)
        print("\n===========================\n")

        print("Resume Length:", len(resume_text))

        score, matched_skills, missing_skills = analyze_resume(
            resume_text,
            job_role
        )

        all_skills = extract_all_skills(
         resume_text
        )

        role_scores, best_role = compare_all_roles(
        resume_text
        )

        if score >= 80:
            suggestion = "Excellent match! Your resume aligns very well with the selected role."
        elif score >= 60:
            suggestion = "Good match. Add more role-specific projects and skills."
        else:
            suggestion = "Resume needs improvement. Focus on missing skills and relevant projects."
        print("Role Scores:", role_scores)
        print("Best Role:", best_role)
        print("All Skills:", all_skills)
        
        return render_template(
    "dashboard.html",

    score=score,

    matched_skills=", ".join(matched_skills)
    if matched_skills else "No matching skills found",

    missing_skills=", ".join(missing_skills)
    if missing_skills else "None",

    all_skills=", ".join(all_skills)
    if all_skills else "No skills detected",

    role_scores=role_scores,

    best_role=best_role,

    suggestions=suggestion
)

    except Exception as e:
        return f"Error processing resume: {str(e)}"


# =====================================
# RUN APP
# =====================================
if __name__ == "__main__":
    app.run(debug=True)