# 📄 Smart Placement Analyzer

A web application that analyzes resumes and provides ATS scores, skill detection, and job role recommendations — powered by AWS.

🌐 **Live Demo:** [Smart Placement Analyzer](http://smartplacement-env2.eba-arnzympg.eu-north-1.elasticbeanstalk.com)

---

## 🚀 Features

- 📤 Upload resume (PDF) and get instant analysis
- 🎯 ATS Score calculation based on selected job role
- 🛠 Skill detection from resume content
- ✅ Matched and ❌ Missing skills breakdown
- 🏆 Best fit job role recommendation
- 📊 Role comparison with visual progress bars
- 💡 Personalized recommendations
- 💾 Full upload history saved to AWS DynamoDB (per-student timeline, not overwritten)
- 📧 Automated email report sent via AWS SES
- 🌐 Deployed live on AWS Elastic Beanstalk

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML, CSS, Bootstrap 5 |
| PDF Parsing | PyPDF2 |
| Cloud Storage | AWS S3 |
| Database | AWS DynamoDB |
| Deployment | AWS Elastic Beanstalk |
| Environment | Python 3.12, Amazon Linux 2023 |

---

## ☁️ AWS Services Used

- **S3** — Stores uploaded resume PDFs
- **DynamoDB** — Stores every resume analysis as a separate record using `email` (partition key) + `uploaded_at` (sort key), preserving full upload history per student
- **Elastic Beanstalk** — Hosts and runs the Flask application

---

## 📁 Project Structure

SmartPlacementAnalyzer/

├── app.py                  # Flask backend

├── Procfile                # Gunicorn startup command

├── requirements.txt        # Python dependencies

├── .env                    # Environment variables (not pushed)

├── .ebignore               # Files excluded from EB deployment

├── .gitignore              # Files excluded from Git

├── static/

│   └── style.css           # Custom styles

└── templates/

├── index.html          # Upload form

└── dashboard.html      # Analysis results dashboard

---

## ⚙️ Environment Variables

Create a `.env` file in the root directory:

```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=eu-north-1
BUCKET_NAME=your_s3_bucket_name
```

---

## 🏃 Run Locally

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/SmartPlacementAnalyzer.git
cd SmartPlacementAnalyzer
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up `.env` file** with your AWS credentials

4. **Run the app**
```bash
python app.py
```

5. **Open in browser**
http://127.0.0.1:5000

---

## 🚀 Deploy to AWS Elastic Beanstalk

1. **Initialize EB**
```bash
eb init
```

2. **Create environment**
```bash
eb create smartplacement-env2
```

3. **Set environment variables**
```bash
eb setenv AWS_ACCESS_KEY_ID=your_key AWS_SECRET_ACCESS_KEY=your_secret AWS_REGION=eu-north-1 BUCKET_NAME=your_bucket
```

4. **Deploy updates**
```bash
eb deploy smartplacement-env2
```

---
## 📧 Email Reports (AWS SES)

After analysis, students automatically receive an email with:
- ATS Score
- Matched & Missing Skills
- Best Fit Role
- Recommendations

> **Note:** AWS SES is currently in **Sandbox Mode**, so emails can only be sent to verified email addresses. To send to any recipient, request **Production Access** in the AWS SES console.

---

## 📊 Supported Job Roles

- Software Engineer
- Web Development
- Cyber Security Analyst
- Cloud Engineer

---

## 🗂 Database Design

The `StudentsHistory` table uses a composite key:
- **Partition key:** `email`
- **Sort key:** `uploaded_at`

This allows each student to have multiple resume analyses stored over time instead of overwriting previous results — enabling a complete history of their progress.

---

## 🔮 Planned Features

- 📄 Better PDF parsing with AWS Textract
- 🔐 User authentication with AWS Cognito
- 🌍 Custom domain name

---

## 👩‍💻 Author

**Avani J C**  
[GitHub](https://github.com/Avani24-byte)



