# QuizApp — Flask + Vue 3 Quiz Management & Taking Platform

A full-featured quiz platform where **Administrators** manage subjects, chapters, quizzes, and questions; and **Users** attempt quizzes under timed conditions, track their performance, and visualize progress—all through a responsive UI and a documented RESTful API.

---

## Table of Contents

- [1. Introduction](#1-introduction)
- [2. Features](#2-features)
  - [2.1. Core Features](#21-core-features)
  - [2.2. Admin Features](#22-admin-features)
  - [2.3. User Features](#23-user-features)
  - [2.4. API & Documentation](#24-api--documentation)
- [3. Technology Stack](#3-technology-stack)
- [4. Setup and Installation](#4-setup-and-installation)
- [5. Usage](#5-usage)
  - [5.1. Admin User](#51-admin-user)
  - [5.2. Regular User](#52-regular-user)
- [6. API Documentation](#6-api-documentation)
  - [6.1. Authentication Model](#61-authentication-model)
  - [6.2. Base URL](#62-base-url)
  - [6.3. Main Resources](#63-main-resources)
  - [6.4. Example Payloads](#64-example-payloads)
- [7. Bulk Data Upload](#7-bulk-data-upload)
- [8. Project Structure (Suggested)](#8-project-structure-suggested)
- [9. Environment Variables (Suggested)](#9-environment-variables-suggested)
- [10. Data Model Overview (Conceptual)](#10-data-model-overview-conceptual)
- [11. Security Notes](#11-security-notes)
- [12. Known Limitations & Roadmap](#12-known-limitations--roadmap)
- [13. License](#13-license)

---

## 1. Introduction

**QuizApp** is a web application built with **Flask** that allows administrators to create and manage **subjects, chapters, quizzes, and questions**. Registered users can then browse available quizzes, attempt them under **timed** conditions, and view their performance history and summary statistics. The application features distinct roles for **Admins** and regular **Users**, a responsive web interface using **Bootstrap 5** (with **Vue 3** for interactivity), and a **RESTful API** for programmatic management (documented with **Swagger UI**).

---

## 2. Features

### 2.1. Core Features

- **Role-Based Access Control:** Clear distinction between **Administrators** (full content management) and **Users** (quiz taking and viewing own results).
- **Session-Based Authentication:** Secure user login, registration, and session management using **Flask-Login**. Includes basic (stubbed) “Forgot Password” functionality.
- **Beautiful and Responsive UI:** User interface built with **Vue 3** and **Bootstrap 5**, designed to work across different screen sizes.
- **Scheduled Jobs & Caching:** Background tasks and caching have been implemented to improve performance and enable recurring maintenance (e.g., refreshing cached lists, precomputing summary stats).

### 2.2. Admin Features

- **Admin Dashboard:** Interactive dashboard using accordions to manage educational content.
  - **Subject Management:** Create, Read, Update, Delete (CRUD) subjects.
  - **Chapter Management:** CRUD chapters nested within their respective subjects.
  - **Quiz Management:** View quizzes nested within chapters; Add/Edit/Delete quizzes (linking to dedicated forms/pages).
- **Quiz Question Management:** Dedicated interface (linked from quiz lists) to CRUD **Multiple Choice Questions (MCQ)** with exactly **4 options** for any given quiz. Mark the correct answer.
- **All Quizzes View:** A separate page listing all quizzes in the system with filtering/sorting options (implicit).
- **Admin Summary & Reports:**
  - Visual charts (Bar, Doughnut via **Chart.js**) showing:
    - Highest scores achieved per subject across all users.
    - Total quiz attempts per subject.
    - Number of quizzes per subject.
  - Content overview statistics (total users, subjects, chapters, etc.).
  - User activity ranking table based on the number of quiz attempts, with links to detailed user activity.
  - List of quizzes that currently have **no questions** added.
- **Search Functionality:** Dedicated search page to find Users (by username/email), Subjects (by name/description), and Quizzes (by title).

### 2.3. User Features

- **User Dashboard:** Browse available active quizzes, organized by Subject and Chapter using an accordion interface. View **highest achieved score** on previously attempted quizzes.
- **Quiz Taking:**
  - Interactive interface for attempting quizzes one question at a time.
  - **Countdown timer** based on the quiz duration.
  - Immediate answer checking (“Check” button) with visual feedback (correct/incorrect highlighting).
  - Navigation between questions (**Previous/Next**).
  - Final submission (manual or automatic on **timeout**).
- **User Summary:**
  - View history of past quiz attempts, including score, percentage, date, and time taken.
  - View personal performance charts (e.g., **highest scores per subject**, **attempts per subject**).

### 2.4. API & Documentation

- **RESTful API:** Provides endpoints (`/api/...`) for programmatic CRUD operations on most data models (**Subjects, Chapters, Quizzes, Questions, Users, Roles, Attempts**).
- **Swagger UI:** Integrated API documentation available at **`/apidocs/`**, automatically generated using **Flasgger**.

---

## 3. Technology Stack

| Layer          | Technology                                                                                         |
|----------------|----------------------------------------------------------------------------------------------------|
| **Backend**    | Python 3, Flask                                                                                    |
| **Frameworks** | Flask (server), **Vue 3** (frontend interactivity)                                                 |
| **Database**   | SQLAlchemy ORM (**SQLite** by default in development)                                              |
| **Auth**       | **Flask-Login** (Session-based)                                                                    |
| **Security**   | Werkzeug Security Utilities (password hashing)                                                     |
| **API**        | Flask-RESTful                                                                                      |
| **Docs**       | **Flasgger (Swagger UI)**                                                                          |
| **Frontend**   | Vue 3 (templating/interaction), **Bootstrap 5** (CSS), JavaScript (quiz logic, charts)             |
| **Charts**     | **Chart.js**                                                                                       |
| **Performance**| Caching + Scheduled Jobs (e.g., Flask-Caching/APScheduler if enabled)                              |

> See `requirements.txt` for specific Python package dependencies.

---

## 4. Setup and Installation

1. **Prerequisites**
   - Python **3.8+**
   - `pip` package installer
   - Node.js (for Vue 3 dev tooling) if running a separate frontend workflow

2. **Create Virtual Environment**  
    (Linux/macOS)
    
        python -m venv venv
        source venv/bin/activate

    (Windows)

        python -m venv venv
        venv\Scripts\activate

3. **Install Requirements**
    
        pip install -r requirements.txt

4. **Frontend Setup (Vue 3)**
    
        cd frontend
        npm install
        npm run dev

> Depending on your setup, the Vue dev server may proxy API calls to Flask at `http://127.0.0.1:5000`.

---

## 5. Usage

### 5.1. Admin User

1. Navigate to **`http://127.0.0.1:5000/login`** (or the root `/`).
2. Log in using the configured admin credentials (default):  
   - **username:** `admin`  
   - **password:** `Thisisadmin@123!`
3. You will be redirected to the **Admin Dashboard** (`/admin/dashboard`).
4. **Manage Content:**
   - Use the **“Add New Subject”** form.
   - Expand subjects using the accordion buttons.
   - **Add/Edit/Delete Chapters** within a subject’s expanded view.
   - Click the **“Quizzes”** button next to a chapter to expand the quiz list for that chapter.
   - **Add/Edit/Delete Quizzes** within the chapter’s quiz list, or via the **“All Quizzes”** page.
   - Click the **“Questions”** button next to a quiz (in the nested list or on the **“All Quizzes”** page) to navigate to the **Question Management** page for that quiz.
   - **Add/Edit/Delete MCQs** with **4 options** on the Question Management page.
5. **View Reports:**
   - Navigate to the **“Summary”** page via the navbar to see charts and statistics.
   - View **“All Quizzes”** via the navbar link.
   - Use the **“Search”** page to find Users/Subjects/Quizzes.

### 5.2. Regular User

1. Navigate to **`http://127.0.0.1:5000/login`**.
2. Click **“Create an Account”** to open the registration modal. Fill in details and register. You will be logged in automatically.  
   *(Or)* Log in with existing user credentials (e.g., `user000` / `User000@123`).
3. You will be redirected to the **User Dashboard** (`/dashboard`).
4. Browse **Subjects/Chapters** using the accordions.
5. Click **“Attempt Quiz”** on an active quiz card.
6. **Take the Quiz:**
   - Note the **timer**.
   - Select an answer for the current question.
   - Click **“Check Answer”** to see immediate feedback (correct/incorrect highlighting). Radios will be disabled.
   - Click **“Next”** (or **“Previous”** after checking) to navigate.
   - Click **“Submit Quiz”** on the last question **or** let the timer expire for **auto-submission**.
7. After submission, you are redirected to **My Summary** (`/dashboard/summary`).
8. View **past attempts** and **performance charts** on the summary page.

> **User Quiz Flow (Conceptual)**
>
> ~~~~mermaid
> flowchart LR
>   A[Browse Quizzes] --> B[Start Quiz]
>   B --> C[Question 1..N]
>   C -->|Check Answer| D{Correct?}
>   D -- Yes --> E[Highlight Correct]
>   D -- No --> F[Highlight Incorrect]
>   E --> G[Next/Prev]
>   F --> G[Next/Prev]
>   G --> H{Timer Expired or Submit?}
>   H -- Submit --> I[Evaluate & Save Attempt]
>   H -- Expired --> I[Auto-Submit & Save]
>   I --> J[Show Results & Summary]
> ~~~~

---

## 6. API Documentation

### 6.1. Authentication Model
- The API currently relies on the **same session-based authentication** as the web application.
- Clients **must authenticate** via the web login (`/login`) first and then **include the session cookie** in the `Cookie` header of subsequent API requests.
- **CSRF protection is disabled** for the API blueprint prefix (`/api`) to simplify programmatic access.

### 6.2. Base URL
- **Local Development:** `http://127.0.0.1:5000/api`

### 6.3. Main Resources

| Resource                                 | Methods              | Notes                                           |
|------------------------------------------|----------------------|-------------------------------------------------|
| `/subjects`                              | GET, POST            | List/Create subjects                            |
| `/subjects/{subject_id}`                 | GET, PUT, DELETE     | Retrieve/Update/Delete a subject                |
| `/chapters`                              | GET, POST            | List/Create chapters                            |
| `/chapters/{chapter_id}`                 | GET, PUT, DELETE     | Retrieve/Update/Delete a chapter                |
| `/quizzes`                               | GET, POST            | List/Create quizzes                             |
| `/quizzes/{quiz_id}`                     | GET, PUT, DELETE     | Retrieve/Update/Delete a quiz                   |
| `/quizzes/{quiz_id}/questions`           | GET, POST            | List/Create questions for a quiz                |
| `/questions/{question_id}`               | GET, PUT, DELETE     | Retrieve/Update/Delete a question               |
| `/attempts`                              | GET, POST            | List user attempts / Create a new attempt       |
| `/attempts/{attempt_id}`                 | GET                  | Retrieve a specific attempt                     |
| `/users` *(Admin only)*                  | GET, POST            | List/Create users                               |
| `/users/{user_id}` *(Admin only)*        | GET, PUT, DELETE     | Retrieve/Update/Delete a user                   |
| `/roles` *(Admin only)*                  | GET, POST            | List/Create roles                               |
| `/roles/{role_id}` *(Admin only)*        | GET, PUT, DELETE     | Retrieve/Update/Delete a role                   |

> **Swagger UI**: Visit **`/apidocs/`** to explore endpoints, see schemas, and test requests.

### 6.4. Example Payloads

**Create Subject**
    
    {
      "name": "Mathematics",
      "description": "Core math fundamentals"
    }

**Create Chapter**
    
    {
      "subject_id": 1,
      "name": "Algebra I",
      "description": "Linear equations and inequalities"
    }

**Create Quiz**
    
    {
      "chapter_id": 1,
      "title": "Linear Equations Basics",
      "duration_minutes": 15,
      "is_active": true
    }

**Create Question (MCQ with 4 options)**
    
    {
      "quiz_id": 1,
      "prompt": "What is the solution to 2x + 3 = 11?",
      "options": ["3", "4", "5", "6"],
      "correct_index": 1
    }

**Submit Attempt**
    
    {
      "quiz_id": 1,
      "answers": [1, 0, 3, 2],
      "started_at": "2025-08-01T10:00:00Z",
      "submitted_at": "2025-08-01T10:12:30Z"
    }

---

## 7. Bulk Data Upload

- A script **`upload_initial_data.py`** is provided to bulk-load **Subjects, Chapters, Quizzes, and Questions** from corresponding `.csv` files.

**Usage**
1. Ensure the Flask app is **running**.
2. **Log in** as admin via the web browser.
3. **Copy the session cookie** value from browser developer tools.
4. Run:
    
        python upload_initial_data.py

5. **Paste the session cookie** value when prompted.

> The script requires the **`requests`** library (`pip install requests`).

---

