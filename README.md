<div align="center">

# 🪺 HireNest
### *Connecting Talent*

**A Smart AI Based Hiring and Recruitment Platform**

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white) ![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black) ![Python](https://img.shields.io/badge/Python_Flask-000000?style=for-the-badge&logo=flask&logoColor=white) ![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)

*A Project Submitted for **ST4005CMD - Integrative Project***
*Softwarica College of IT and E-Commerce — Computer Science with AI*

</div>

---

## 📌 Table of Contents
- [About the Project](#-about-the-project)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [System Architecture](#-system-architecture)
- [Getting Started](#-getting-started)
- [Folder Structure](#-folder-structure)
- [Development Methodology](#-development-methodology)
- [Team Members](#-team-members)
- [Project Links](#-project-links)

---

## 📖 About the Project

In today's digital world, finding a suitable job has become difficult for many students, fresh graduates, and skilled people — while companies also struggle to find qualified employees on time. Traditional hiring systems are slow and confusing: job information is scattered, applications are checked manually, and communication is not smooth.

**HireNest** is a smart, user-friendly online job portal that bridges this gap. It connects job seekers and employers on a single platform where users can register, create profiles, search and apply for jobs, track applications, and receive notifications — while employers can post vacancies, manage listings, and find the right candidates efficiently.

> *"Making job searching, job posting, applying, and hiring faster, easier, and more organized."*

---

## ✨ Features

### 👤 Core Experience
- User registration, login, logout, and profile management
- Employers can post, update, and delete job listings
- Job seekers can search, save, and apply for jobs

### 🤖 Smart Job Matching
- AI-based job suggestions based on user skills and interests
- Filter jobs by location, salary, and experience level

### 📊 Application Tracking
- Track application status: **Applied → Shortlisted → Rejected → Selected**
- Real-time notifications for application updates

### 💬 Communication System
- Direct messaging between employers and job seekers
- Interview scheduling feature

### 📄 Resume & Profile Management
- Upload and update resumes
- Build and customize professional profiles

### 🔔 Job Alerts
- Notifications for new job postings matching user preferences
- Save job alerts for later review

### 🛡️  Dashboard
- Manage users, job posts, and overall platform activity

---

## 🛠 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | HTML5, CSS3, JavaScript | UI structure, styling, and interactivity |
| Backend | Python (Flask) | Server-side logic and API |
| Database | MySQL | Data storage and management |
| UI Design | Figma | Prototyping and design mockups |
| Version Control | Git & GitHub | Source code management |
| Task Management | Trello | Sprint planning and tracking |
| Diagrams | Draw.io | ER diagrams and system design |
| IDE | Visual Studio Code | Development environment |
| Communication | Google Meet / MS Teams | Team collaboration |

---

## 🏗 System Architecture

| Layer | Components |
|-------|-----------|
| 👥 Users | Job Seekers & Employers |
| ⚙️ Core Platform | User Auth, Job Posting, Search Engine, Application Tracking, Notifications |
| 🗄️ Database | User Profiles, Job Listings, Applications, Resumes, Company Data |
| 🤖 AI Layer (Optional) | AI Job Recommendations, Resume Suggestions |

---

## 🚀 Getting Started

### Prerequisites
- [Python 3.8+](https://www.python.org/downloads/)
- [MySQL](https://www.mysql.com/downloads/)
- [Git](https://git-scm.com/)

### Installation

**1. Clone the repository**

    git clone https://github.com/ArunSth/ArunSth-AI39B-Group-7-HireNest.git
    cd ArunSth-AI39B-Group-7-HireNest

**2. Create and activate a virtual environment**

    # Windows
    python -m venv venv
    venv\Scripts\activate

    # macOS / Linux
    python3 -m venv venv
    source venv/bin/activate

**3. Install dependencies**

    pip install -r requirements.txt

**4. Set up the database**

    CREATE DATABASE hirenest;
    mysql -u root -p hirenest < database/schema.sql

**5. Configure environment variables — create a `.env` file**

    FLASK_APP=app.py
    FLASK_ENV=development
    SECRET_KEY=your_secret_key
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=your_password
    DB_NAME=hirenest

**6. Run the application**

    flask run

**7. Open in your browser:** `http://localhost:5000`

---

## 📁 Folder Structure

    HireNest/
    ├── static/
    │   ├── css/
    │   ├── js/
    │   └── images/
    ├── templates/
    ├── database/
    │   └── schema.sql
    ├── app.py
    ├── requirements.txt
    ├── .env
    └── README.md

---

## 🔄 Development Methodology

HireNest follows the **Agile Software Development Methodology**, structured around sprints:

| Sprint | Focus Area |
|--------|-----------|
| Sprint 1 | User registration & authentication |
| Sprint 2 | Job posting & listing |
| Sprint 3 | Job search & filtering |
| Sprint 4 | Application tracking & notifications |
| Sprint 5 |  dashboard & messaging |
| Sprint 6 | Testing, feedback & final refinements |

---

## 👥 Team Members

| Name | Role |
|------|------|
| **Prayas Banjara** | Developer |
| **Reshuma Shrestha** | Developer |
| **Vijwal Tamang** | Developer |
| **Arun Shrestha** | Leader |
| **Sohan Maharjan** | Developer |

**Submitted to:** Abishek Bimali
**Course:** ST4005CMD — Integrative Project
**Institution:** Softwarica College of IT and E-Commerce
**Submission Date:** 1 May 2026

---

## 🔗 Project Links

| Resource | Link |
|----------|------|
| 🎨 Figma Design | [View Prototype](https://www.figma.com/design/j1AeJROuk0M4qbUoIwTB5s/Untitled?node-id=0-1) |
| 📋 Trello Board | [View Tasks](https://trello.com/invite/b/69e5eb270d47551cbd053e6a/ATTI23e4d9470d5e1cb73bbd1d740cf16d568A84D8B1/hirenest) |
| 📊 Excel Sheet | [View Sheet](https://1drv.ms/x/c/9842f050add3b754/IQBGGgHykfCZSL14CO5Kh1DaAb3t6UoujZlZE6cQ2yZTkKE) |

---

<div align="center">
Made with ❤️ by <b>Group 7 · AI39B</b> — Softwarica College of IT and E-Commerce
</div>
