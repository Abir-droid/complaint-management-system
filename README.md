# 🛠️ Complaint Management System

A lightweight, secure full-stack web application built with **Flask** and **PostgreSQL** that allows users to submit complaints, check status updates, and provides an administrative panel to manage and assign issues.

---

## ✨ Features

* **User Portal:** Submit complaints with automatic phone number validation (7–15 digits) and instant ID generation.
* **Status Tracker:** Search and view real-time complaint status and assigned department.
* **Admin Dashboard:** Secure portal to filter, reassign teams, update progress (`Pending`, `Assigned`, `Resolved`, `Closed`), or delete entries.
* **Production Security:** 
  * Rate-limiting on sensitive endpoints via `Flask-Limiter` to prevent brute-force attacks.
  * Encrypted session cookies (`HTTPOnly`, `SameSite`, `Secure`).
  * Environment variable management for database URLs and admin credentials.
* **Database Persistence:** Integrated with **Flask-SQLAlchemy** using PostgreSQL in production and SQLite for local development.

---

## 🚀 Tech Stack

* **Backend:** Python / Flask
* **Database:** PostgreSQL (Render) / SQLite (Local)
* **ORM:** Flask-SQLAlchemy
* **Security:** Flask-Limiter
* **Frontend:** HTML5, CSS3, JavaScript (Fetch API)
* **Hosting:** Render

---

## 🛠️ Local Setup & Installation

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git)
   cd YOUR_REPOSITORY
Create and activate a virtual environment:Bashpython -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
Install dependencies:Bashpip install -r requirements.txt
Run the application locally:Bashpython app.py
Open your browser and navigate to http://127.0.0.1:5000.🔐 Environment VariablesWhen deploying to platforms like Render, ensure the following environment variables are configured in your Web Service dashboard:VariableDescriptionDATABASE_URLPostgreSQL connection string (provided automatically by Render DB).SECRET_KEYLong random string used for session cookie encryption.ADMIN_USERNAMEUsername required to log into the /admin/login panel.ADMIN_PASSWORDPassword required to log into the /admin/login panel.📂 Project StructurePlaintext├── app.py              # Main Flask application logic & API routes
├── requirements.txt    # Python dependencies
├── templates/          # HTML Templates
│   ├── index.html      # Public user portal
│   └── admin.html      # Administrative dashboard
└── README.md           # Project documentation

### 2. Update placeholders
Make sure to replace `YOUR_USERNAME` and `YOUR_REPOSITORY` in the **Local Setup** section with your actual GitHub links!

### 3. Save, Commit, and Push
Run these commands in your VS Code terminal (`Ctrl + ~`):

```bash
git add README.md
git commit -m "add comprehensive project README"
git push