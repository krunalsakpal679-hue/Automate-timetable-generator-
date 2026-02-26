# 📅 Timetable Scheduler System (Django)

A Django-based Timetable Scheduler System designed to automate and manage academic timetable generation efficiently.  
This project focuses on structured scheduling, data management, and conflict-free timetable generation.

---

## 🚀 Project Overview

Creating academic timetables manually is complex and time-consuming.  
This project provides a backend-driven solution using Django that allows users to generate, manage, and view timetables dynamically.

The system follows Django’s MVT architecture and includes custom management commands for timetable generation and sample data creation.

---

## 🛠️ Tech Stack

**Backend**
- Python
- Django

**Frontend**
- HTML
- CSS
- Django Templates

**Database**
- SQLite (default)
- SQL schema included (`schema.sql`)

**Tools**
- Git
- GitHub

---

## ✨ Key Features

- Automated timetable generation
- Custom Django management commands
- Modular Django app structure
- Template-based UI rendering
- Database-driven scheduling logic
- Admin panel support

---

## 📂 Project Structure
timetable-project/
│
├── scheduler/
│ ├── management/
│ │ └── commands/
│ │ ├── create_sample_data.py
│ │ └── generate_timetable.py
│ │
│ ├── migrations/
│ │ ├── 0001_initial.py
│ │ ├── 0002_timetablesettings_alter_.py
│ │ └── 0003_remove_timetablesetting_.py
│ │
│ ├── templates/scheduler/
│ │ ├── add_data.html
│ │ ├── home.html
│ │ └── timetable.html
│ │
│ ├── templatetags/
│ │ ├── dict_utils.py
│ │ └── init.py
│ │
│ ├── admin.py
│ ├── apps.py
│ ├── forms.py
│ ├── generator.py
│ ├── models.py
│ ├── tests.py
│ ├── urls.py
│ └── views.py
│
├── manage.py
├── schema.sql
├── .gitignore
└── README.md
---

## ⚙️ How to Run the Project Locally

### 1️⃣ Clone the repository

git clone https://github.com/krunalsakpal679-hue/Automate-timetable-generator-.git

cd timetable-project


---

### 2️⃣ Create and activate virtual environment

python -m venv venv
venv\Scripts\activate


---

### 3️⃣ Install dependencies

pip install django


*(Install additional packages if required)*

---

### 4️⃣ Apply migrations

python manage.py makemigrations
python manage.py migrate


---

### 5️⃣ Create superuser (optional)

python manage.py createsuperuser


---

### 6️⃣ Load sample data (optional)

python manage.py create_sample_data


---

### 7️⃣ Generate timetable

python manage.py generate_timetable


---

### 8️⃣ Run the server

python manage.py runserver


---

### 9️⃣ Open in browser

http://127.0.0.1:8000


---

## 📌 Use Cases

- College and school timetable generation
- Academic scheduling systems
- Faculty workload planning
- Student timetable visualization

---

## 🚀 Future Enhancements

- AI-based timetable optimization
- Role-based authentication
- Export timetable as PDF
- REST API integration
- Cloud deployment

---

## 🤝 Contribution

Contributions are welcome.  
Feel free to fork the repository and submit a pull request.

---

## 📬 Contact

**Developer:** Krunal Sakpal
**Email:** krunalsakpal679@gmail.com  
**LinkedIn:** www.linkedin.com/in/krunal-sakpal  

---

⭐ If you like this project, don’t forget to give it a star on GitHub!