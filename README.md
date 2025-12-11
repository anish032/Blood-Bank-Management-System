# 🩸 Blood Bank Management System

A Django-based web application designed to manage blood donors, blood inventory, donation history, and blood requests between donors and hospitals. Built collaboratively by a team of 5 members using a clean Git workflow.

---

## 🚀 Features

### **Donor Module**

* Donor registration & login
* Donor profile management
* Blood group & availability status
* Donation history tracking

### **Hospital / Organization Module**

* Hospital user login
* Request blood units
* View donor matches
* Track request status (Pending / Approved / Rejected)

### **Admin Module**

* Manage users (donors & hospitals)
* Manage blood inventory
* Approve or reject blood requests
* Dashboard overview with statistics

---

## 📊 Dashboard Overview

The system includes a clean dashboard showing:

* Total donors
* Blood groups & available units
* Pending / approved requests
* Recent donations
* System activity summary

---

## 🛠 Tech Stack

* **Backend:** Django (Python)
* **Frontend:** HTML, CSS, Bootstrap 5
* **Database:** SQLite (development), MySQL/PostgreSQL (optional)
* **Version Control:** Git + GitHub

---

## 📁 Project Structure (Typical Django Layout)

```
blood-bank-project/
│
├── bloodbank/           # Main Django project
├── dashboard/           # Dashboard app
├── donor/               # Donor module
├── hospital/            # Hospital module
├── inventory/           # Blood inventory module
├── requirements.txt     # Dependencies
├── manage.py
└── README.md
```

---

## 🏁 Getting Started (For Developers)

Follow these steps to run the project locally.

### **1️⃣ Clone the repository**

```bash
git clone <repo-url>
cd <repo-folder>
```

### **2️⃣ Create & activate virtual environment**

```bash
python -m venv env
env\Scripts\activate
```

### **3️⃣ Install dependencies**

```bash
pip install -r requirements.txt
```

### **4️⃣ Apply migrations**

```bash
python manage.py migrate
```

### **5️⃣ Run the development server**

```bash
python manage.py runserver
```

Access the site at:
**[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🤝 Contributing

We follow a structured workflow using feature branches and pull requests.

### **Basic Workflow**

1. Pull latest main:

   ```bash
   git checkout main
   git pull origin main
   ```
2. Create your feature branch:

   ```bash
   git checkout -b feature/your-feature
   ```
3. Add & commit your changes:

   ```bash
   git add .
   git commit -m "Add new dashboard UI"
   ```
4. Push your branch:

   ```bash
   git push origin feature/your-feature
   ```

## 👥 Team

This project is developed by a team of **5 contributors**, following best Git practices and collaborative workflow.

---

## ⭐ Support

If you find this project helpful, consider starring the repository!

For improvements or suggestions, feel free to open an Issue or Pull Request.
