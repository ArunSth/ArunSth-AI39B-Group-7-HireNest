<div align="center">

# 🪺 HireNest
### *Connecting Talent*

**A Smart AI Based Hiring and Recruitment Platform**

![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)
![Python](https://img.shields.io/badge/Python-Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)

*ST4005CMD – Integrative Project*  
*Softwarica College of IT and E-Commerce*  
*BSc (Hons) Computer Science with AI*

</div>

---

# 📌 Table of Contents

- About the Project
- Features
- User Roles
- Tech Stack
- System Architecture
- Getting Started
- Project Structure
- Development Methodology
- Screenshots
- Team Members
- Project Links

---

# 📖 About the Project

HireNest is a web-based hiring and recruitment platform designed to connect job seekers and employers through a centralized system.

The platform simplifies the recruitment process by allowing employers to post vacancies, manage applications, schedule interviews, and communicate with candidates. Job seekers can search for jobs, save opportunities, apply online, track applications, and receive notifications regarding their hiring progress.

HireNest aims to make job searching, job posting, and recruitment faster, easier, and more organized.

---

# ✨ Features

## 👤 Authentication & User Management

- User Registration
- Secure Login & Logout
- Role-Based Access Control
- Profile Management
- Profile Completion Tracking

---

## 💼 Job Management

### For Employers

- Create Job Listings
- Update Job Listings
- Delete Job Listings
- Manage Applications
- Track Applicants
- Schedule Interviews

### For Job Seekers

- Search Jobs
- Filter Jobs
- View Job Details
- Apply for Jobs
- Save Jobs
- Track Application Status

---

## 📊 Application Tracking

Track applications through stages:

- Applied
- Under Review
- Shortlisted
- Rejected
- Hired

---

## 💬 Communication System

- In-App Messaging
- Employer-Candidate Communication
- Interview Invitations
- Interview Scheduling

---

## ⭐ Company Reviews

- Submit Reviews
- Company Ratings
- Public Review Visibility

---

## 🔔 Notifications

- Application Updates
- Interview Notifications
- Message Alerts
- Job Alerts

---

## 🚨 Job Reporting & Moderation

### Job Seekers

- Report Suspicious Jobs
- Flag Inappropriate Listings

### Admin

- Review Reported Jobs
- Moderate Job Listings
- Approve or Remove Jobs

---

## 💳 Employer Subscription System

- Subscription Plans
- Payment Tracking
- Payment History
- Plan Management

---

## 🛡️ Admin Dashboard

- User Management
- Job Moderation
- Company Reviews Management
- Reported Jobs Management
- Platform Analytics
- System Monitoring

---

# 👥 User Roles

## Job Seeker

- Create Profile
- Upload Resume
- Search Jobs
- Save Jobs
- Apply for Jobs
- Track Applications
- Review Companies
- Receive Notifications

## Employer

- Manage Company Profile
- Post Jobs
- Manage Applicants
- Schedule Interviews
- View Subscription Plans
- View Payment History

## Admin

- Manage Users
- Moderate Jobs
- Handle Reports
- Monitor Platform Activity
- Manage Reviews

---

# 🛠️ Tech Stack

| Layer | Technology |
|---------|------------|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python, Flask |
| Templates | Jinja2 |
| Database | MySQL |
| Database Tool | MySQL Workbench |
| UI Design | Figma |
| Version Control | Git & GitHub |
| Task Management | Trello |
| Diagrams | Draw.io |
| IDE | Visual Studio Code |

---

# 🏗️ System Architecture

## Users

- Job Seekers
- Employers
- Admin

## Core Platform

- Authentication System
- Job Management
- Search Engine
- Application Tracking
- Messaging System
- Notifications
- Reviews & Ratings

## Database Layer

- Users
- Companies
- Jobs
- Applications
- Resumes
- Interviews
- Reviews
- Notifications

## Recommendation Layer

- Skill-Based Job Suggestions
- Personalized Recommendations

---

# 🚀 Getting Started

## Prerequisites

- Python 3.8+
- MySQL Server
- Git

---

## Installation

### Clone Repository

bash
git clone https://github.com/ArunSth/ArunSth-AI39B-Group-7-HireNest.git
cd ArunSth-AI39B-Group-7-HireNest


### Create Virtual Environment

Windows

bash
python -m venv venv
venv\Scripts\activate


Linux / Mac

bash
python3 -m venv venv
source venv/bin/activate


### Install Dependencies

bash
pip install -r requirements.txt


### Create Database

sql
CREATE DATABASE hirenest;


### Configure Environment Variables

Create a .env file:

env
FLASK_APP=app.py
FLASK_ENV=development

SECRET_KEY=your_secret_key

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=@Password1
DB_NAME=hirenest


### Run Application

bash
flask run


Application URL:

text
http://localhost:5000


---

# 📁 Project Structure

text
HireNest/
│
├── app/
│   ├── controllers/
│   ├── routes/
│   ├── modals/
│   ├── templates/
│   ├── statics/
│   └── utils/
│
├── uploads/
│   ├── logos/
│   ├── resumes/
│   └── profile_pictures/
│
├── tests/
│
├── requirements.txt
├── app.py
└── README.md


---

# 🔄 Development Methodology

The project follows the Agile Software Development Methodology.

| Sprint | Focus Area |
|----------|----------|
| Sprint 1 | User Registration & Authentication |
| Sprint 2 | Employer Profile & Company Setup |
| Sprint 3 | Job Posting & Job Search |
| Sprint 4 | Applications & Tracking |
| Sprint 5 | Messaging & Interviews |
| Sprint 6 | Reviews, Notifications & Alerts |
| Sprint 7 | Admin Dashboard & Moderation |
| Sprint 8 | Testing & Bug Fixing |

---

# 📸 Screenshots

## Home Page

(Add Screenshot)

## Job Seeker Dashboard

(Add Screenshot)

## Employer Dashboard

(Add Screenshot)

## Admin Dashboard

(Add Screenshot)

---

# 🧪 Testing

The project includes unit testing for controller logic using Python's unittest framework.

Run tests:

bash
python -m unittest discover tests


Or:

bash
pytest


---

# 👥 Team Members

| Name | Role |
|--------|--------|
| Arun Shrestha | Team Leader |
| Prayas Banjara | Developer |
| Reshuma Shrestha | Developer |
| Vijwal Tamang | Developer |
| Sohan Maharjan | Developer |

---

# 👨‍🏫 Submitted To

*Abishek Bimali*

*ST4005CMD – Integrative Project*

*Softwarica College of IT and E-Commerce*

---

# 🔗 Project Links

### 🎨 Figma

https://www.figma.com/design/j1AeJROuk0M4qbUoIwTB5s/Untitled

### 📋 Trello

https://trello.com/invite/b/69e5eb270d47551cbd053e6a

### 📊 Project Spreadsheet

https://1drv.ms/x/c/9842f050add3b754

---

<div align="center">

### ❤️ Made with dedication by Group 7

*HireNest — Connecting Talent with Opportunity*

</div>