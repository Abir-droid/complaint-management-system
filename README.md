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
