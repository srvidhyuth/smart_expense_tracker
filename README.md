# 💰 Smart Expense Tracker

A full-featured Expense Tracking application built with **Python**, **Flask**, **Tkinter**, and **MongoDB Atlas**. It allows users to record, manage, and analyze daily expenses via either a modern **Web Interface** or a **Desktop GUI App**.

---

## 🌟 Key Features

- ➕ **Add Expenses**: Easily log daily expenses with Date, Description, Amount, and Category.
- 📋 **View Expenses**: Interactive expense log with sortable records.
- ✏️ **Edit & Update**: Select any expense to modify its details.
- ❌ **Delete Expenses**: Remove entries with real-time database syncing.
- 📊 **Expense Analytics**: Displays total spent and detailed category-wise breakdowns.
- 🌐 **Dual Interface**:
  - **Web Application**: Built with Flask, HTML5, CSS3, and JavaScript.
  - **Desktop Application**: Built with Python Tkinter GUI.
- ☁️ **Cloud Database Connection**: Powered by MongoDB Atlas with `.env` configuration support.

---

## 🛠️ Tech Stack

- **Backend**: Python 3, Flask, PyMongo, python-dotenv
- **Frontend**: HTML5, Vanilla CSS3, JavaScript (Fetch API)
- **Desktop UI**: Python Tkinter
- **Database**: MongoDB Atlas (or Local MongoDB)

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.8 or higher installed on your system.
- A free [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) cluster account (or local MongoDB).

### 2. Installation
Clone the repository to your local machine:
```bash
git clone <YOUR_GITHUB_REPO_URL>
cd smart_expense_tracker
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and replace the `MONGO_URI` with your own MongoDB Atlas connection string:
   ```env
   MONGO_URI=mongodb+srv://<username>:<password>@cluster0.mongodb.net/?appName=Cluster0
   ```

> ⚠️ **Note**: Make sure your IP address is whitelisted in MongoDB Atlas under **Security ➔ Network Access**.

---

## 🏃 Running the Application

### Option A: Web Application (Flask)
Run the Flask server:
```bash
python app.py
```
Open your web browser and navigate to: **`http://127.0.0.1:5000`**

### Option B: Desktop GUI Application (Tkinter)
Run the desktop window:
```bash
python expense_tracker.py
```

---

## 📁 Project Structure

```text
smart_expense_tracker/
├── app.py                # Flask Web Server & API Routes
├── expense_tracker.py    # Tkinter Desktop GUI Application
├── requirements.txt      # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore            # Git ignore file (hides sensitive credentials)
├── README.md             # Project documentation
└── static/               # Web Application static assets
    ├── index.html        # Web UI structure
    ├── css/style.css     # Styling & Theme
    └── js/script.js      # Frontend logic & API calls
```

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
