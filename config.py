# ============================================================
#  config.py  –  All user-configurable settings live here
# ============================================================
import os
from dotenv import load_dotenv

load_dotenv()

# ── Job Search ───────────────────────────────────────────────
JOB_KEYWORDS   = "Software Engineer, Mean Stack Developer, Mern Stack Developer, Full Stack Developer"          # role to search for
JOB_LOCATION   = "India"                      # city / country / "Remote"
MAX_PAGES      = 3                            # pages to scrape per platform
MIN_MATCH_PCT  = 40                           # only email jobs above this %

# ── Platforms to enable ──────────────────────────────────────
ENABLE_LINKEDIN = True
ENABLE_INDEED   = True
ENABLE_NAUKRI   = True

# ── Gmail SMTP ───────────────────────────────────────────────
GMAIL_SENDER    = os.getenv("GMAIL_SENDER", "your_email@gmail.com")
GMAIL_PASSWORD  = os.getenv("GMAIL_PASSWORD", "")           # Gmail App Password (NOT account pw)
NOTIFY_EMAIL    = os.getenv("NOTIFY_EMAIL", "your_email@gmail.com")

# ── Resume (paste your resume text between the triple-quotes) ─
RESUME_TEXT = """
Name: Yaswanth Narayana Pilla
Role: Software Development Engineer (Full-Stack) | 2+ Years Experience
Contact: +91 7095673438 | yaswanthnarayana3438@gmail.com | yaishwanthnarayana.pilla@gmail.com

SUMMARY:
Full-stack product engineer with 2+ years building and shipping Angular + Node.js platforms at scale.
Delivered measurable wins: slashed listing API latency from 3s to under 800ms, achieved 90% PDF compression,
authored CI/CD pipelines and AWS SAM deployments, and engineered tree-based and divide-and-conquer algorithms
running in production. Thrives in product-company environments where ownership means shipping the feature,
the infra, and the fix.

SKILLS:
- Languages: JavaScript, TypeScript, Python, C++, SQL, HTML, CSS
- Frontend: React, Angular 15+, Angular Material, Material UI, ECharts.js, Bootstrap
- Backend: Node.js, NestJS, Express.js, RESTful APIs, gRPC, Socket.io, JWT, Exotel, e-sign SDKs
- Databases: MongoDB, SQL, Redis, Atlas Vector Search
- Cloud/DevOps: AWS (Lambda, EC2, SAM, CloudFront, SNS, SQS, Bedrock), Docker, CI/CD Pipelines, Git, npm
- Testing & Tools: Mocha, Chai, Swagger/OpenAPI, Voyage AI
- Algorithms: Recursion, Divide & Conquer, Custom Tree Traversal, Config-driven rendering
- Methodology: Agile, Scrum

EXPERIENCE:
1. Product Developer | InnCircles | Hyderabad | Aug 2023 – Present
   - Reduced listing API latency 73% (3s → 700ms) via backend query rewrite + AWS Lambda + SAM IaC templates
   - Built customer-facing resident portal serving 3,000–4,000 active users (payments, documents, support)
   - Built interactive ECharts.js dashboards for payment trends, occupancy metrics, and audit trails
   - Conducted end-to-end system audits; fixed bottlenecks and data inconsistencies across backend services
   - Built CI/CD pipelines and Control Centre admin tool for on-demand server provisioning
   - Integrated Exotel for WhatsApp messaging + click-to-call; built bulk communication system for executives
   - Achieved 90% PDF compression using lossless pipeline; unblocked reliable large-document email delivery
   - Integrated Bank Payment APIs for real-time auto-reconciliation; eliminated manual payment-logging lag
   - Automated e-signing lifecycle via third-party SDK (days → hours document turnaround)
   - Built payment-schedule engine with auto-trigger demand notices (zero missed payment prompts)
   - Built config-driven recursive JSON Form Builder (new forms in minutes, not days)
   - Implemented O(1) folder-tree system using custom tree algorithm for document management
   - Applied divide-and-conquer for PDF merging on large document sets
   - Resolved 200+ production bugs; introduced Mocha & Chai unit tests; reduced regression rates

2. Full-Stack Developer Intern | MetaComic | Visakhapatnam | May – Jul 2023
   - Built Dine Out restaurant-discovery page end-to-end (responsive UI + live REST APIs, zero post-launch bugs)

PROJECTS:
1. Customer Portal — Angular, Node.js, Express.js, MongoDB, JWT, Socket.io, Bank Payment APIs
   - Self-service portal for flat buyers: payment schedules, flat status, pending items, signed documents
   - Real-time updates via Socket.io; JWT role-based auth; auto-triggered WhatsApp payment notifications

2. Customer Management Admin Portal — Angular, Node.js, AWS Lambda, AWS SAM, MongoDB, Socket.io
   - Full MVC SPA with role-based auth, real-time notifications, advanced search/filter/sort
   - SAM-managed Lambda deployment; resolved 200+ critical bugs

3. Control Centre (Server Provisioning) — Angular, AWS SAM, CI/CD, Node.js
   - Admin tool for non-technical ops to provision servers on demand with automated Lambda deployment

4. Ask Me (RAG AI Assistant) — NestJS, Claude, Voyage AI, MongoDB Atlas Vector Search, Redis, OpenAPI
   - RAG API with SSE streaming; dual-mode agent using 1024-dim embeddings + Atlas Vector Search
   - Persistent multi-turn sessions via Redis; OpenAPI auto-discovery

5. Breathe-X (Respiratory Disease Predictor) — React, Node.js, Python, TensorFlow, ResNet50, MongoDB
   - Trained ResNet50 CNN to 96% accuracy on Kaggle pulmonary dataset
   - Live predictions via Node.js API + Python monitoring script to React dashboard

6. Learning Guide (Study Platform) — HTML, CSS, Bootstrap
   - Responsive cross-device study hub with search; adopted by peers for exam prep

EDUCATION:
B.Tech in Computer Science & Engineering
Vignan Institute of Information Technology, Visakhapatnam | GPA: 8.7/10 | 2020–2024

ACHIEVEMENTS:
- Consolation Prize + ₹5,000 | National Level Tech ExtraVaganza, Vignan University
- Top-10 Finalist | National AgriHackathon (100+ teams)
- Top-5 | Coding Contest, ANITS College
- CodeChef 3-star | Active LeetCode competitor
"""

# ── Anthropic API (for AI-powered matching) ──────────────────
# Get your key at https://console.anthropic.com
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
