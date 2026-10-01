"""
School Management System - Self-Contained Flask App
All templates are embedded in the Python file
No external template files needed!
"""

import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# ========================================================
# APP CONFIGURATION
# ========================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(DATA_DIR, "school.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'warning'

# ========================================================
# DATABASE MODELS
# ========================================================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(50), default='admin')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    class_name = db.Column(db.String(50), nullable=False)
    parent_name = db.Column(db.String(100))
    parent_phone = db.Column(db.String(20))
    enrollment_date = db.Column(db.DateTime, default=datetime.utcnow)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(200))
    qualification = db.Column(db.String(100))
    joining_date = db.Column(db.DateTime, default=datetime.utcnow)

class Class(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    section = db.Column(db.String(10))

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(20))
    description = db.Column(db.String(200))

# ========================================================
# USER LOADER
# ========================================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ========================================================
# ALL TEMPLATES AS PYTHON STRINGS
# ========================================================

TEMPLATES = {
    'login.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login - School Management System</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1a3e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        .login-card {
            background: #16213e;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            width: 100%;
            max-width: 420px;
            border: 1px solid #233554;
        }
        .login-card h1 { color: #64ffda; font-weight: bold; font-size: 2rem; }
        .login-card .subtitle { color: #a8b2d1; margin-bottom: 30px; }
        .form-control {
            background: #1a2332;
            border: 2px solid #233554;
            color: #ffffff;
            padding: 12px 15px;
            border-radius: 10px;
        }
        .form-control:focus {
            background: #1a2332;
            border-color: #64ffda;
            color: #ffffff;
            box-shadow: 0 0 0 0.2rem rgba(100, 255, 218, 0.25);
        }
        .form-label { color: #ccd6f6; font-weight: 500; }
        .btn-login {
            background: #64ffda;
            color: #0a0a1a;
            font-weight: bold;
            padding: 12px;
            border: none;
            border-radius: 10px;
            width: 100%;
            font-size: 1.1rem;
            transition: all 0.3s;
        }
        .btn-login:hover {
            background: #4cd3b8;
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(100, 255, 218, 0.2);
        }
        .hint { color: #495670; font-size: 0.85rem; margin-top: 15px; }
        .logo-icon { font-size: 3.5rem; margin-bottom: 10px; }
        .alert { border-radius: 10px; }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="text-center">
            <div class="logo-icon">🏫</div>
            <h1>School Management</h1>
            <p class="subtitle">Login to your account</p>
        </div>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <form method="POST">
            <div class="mb-3">
                <label for="username" class="form-label">Username</label>
                <input type="text" class="form-control" id="username" name="username" 
                       value="admin" required autofocus>
            </div>
            <div class="mb-3">
                <label for="password" class="form-label">Password</label>
                <input type="password" class="form-control" id="password" 
                       name="password" value="admin123" required>
            </div>
            <button type="submit" class="btn-login">🔐 Login</button>
        </form>
        <div class="text-center hint">Default: admin / admin123</div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    ''',
    
    'base.html': '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}School Management System{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #0a0a1a;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            min-height: 100vh;
        }
        .sidebar {
            background: #111128;
            min-height: 100vh;
            padding: 20px 0;
            border-right: 1px solid #1a2d4a;
            position: sticky;
            top: 0;
        }
        .sidebar .logo {
            text-align: center;
            padding: 10px 0 20px;
            border-bottom: 1px solid #1a2d4a;
            margin-bottom: 20px;
        }
        .sidebar .logo h4 { color: #64ffda; font-weight: bold; }
        .sidebar .logo small { color: #8892b0; }
        .sidebar .nav-link {
            color: #a8b2d1;
            padding: 12px 20px;
            margin: 4px 10px;
            border-radius: 10px;
            transition: all 0.3s;
            font-size: 0.95rem;
        }
        .sidebar .nav-link:hover { background: #1a2d4a; color: #ffffff; }
        .sidebar .nav-link.active {
            background: #64ffda;
            color: #0a0a1a;
            font-weight: bold;
        }
        .sidebar .nav-link i { margin-right: 10px; width: 20px; }
        .main-content {
            padding: 25px;
            background: #0a0a1a;
            min-height: 100vh;
        }
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 20px;
            border-bottom: 1px solid #1a2d4a;
            margin-bottom: 25px;
        }
        .top-bar h2 { color: #ffffff; font-weight: bold; }
        .top-bar .subtitle { color: #8892b0; font-size: 0.9rem; }
        .user-info { display: flex; align-items: center; gap: 15px; }
        .user-info .name { color: #ffffff; font-weight: bold; }
        .user-info .role { color: #8892b0; font-size: 0.85rem; }
        .btn-logout {
            background: #e74c3c;
            border: none;
            color: white;
            padding: 8px 20px;
            border-radius: 8px;
            font-weight: bold;
            transition: all 0.3s;
        }
        .btn-logout:hover { background: #c0392b; }
        .card {
            background: #16213e;
            border: none;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .card-title { color: #64ffda; font-weight: bold; }
        .stat-card {
            background: #16213e;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            transition: transform 0.3s;
            border-top: 4px solid #64ffda;
        }
        .stat-card:hover { transform: translateY(-5px); }
        .stat-card .number {
            font-size: 2.5rem;
            font-weight: bold;
            color: #64ffda;
        }
        .stat-card .label {
            color: #a8b2d1;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .table { color: #ccd6f6; }
        .table thead th {
            color: #64ffda;
            border-bottom: 2px solid #233554;
            font-weight: bold;
        }
        .table tbody td {
            border-bottom: 1px solid #1a2d4a;
            vertical-align: middle;
        }
        .table tbody tr:hover { background: #1a2d4a; }
        .btn-primary {
            background: #64ffda;
            border: none;
            color: #0a0a1a;
            font-weight: bold;
        }
        .btn-primary:hover { background: #4cd3b8; color: #0a0a1a; }
        .btn-danger { background: #ff6b6b; border: none; }
        .btn-danger:hover { background: #ee5a24; }
        .btn-warning {
            background: #f39c12;
            border: none;
            color: #0a0a1a;
        }
        .form-control {
            background: #1a2332;
            border: 2px solid #233554;
            color: #ffffff;
            padding: 10px 15px;
            border-radius: 10px;
        }
        .form-control:focus {
            background: #1a2332;
            border-color: #64ffda;
            color: #ffffff;
            box-shadow: 0 0 0 0.2rem rgba(100, 255, 218, 0.25);
        }
        .form-label { color: #a8b2d1; font-weight: 500; }
        .alert { border-radius: 10px; }
        .badge { padding: 5px 12px; border-radius: 20px; }
        .text-muted { color: #8892b0 !important; }
        @media (max-width: 768px) {
            .sidebar { min-height: auto; position: relative; }
            .stat-card .number { font-size: 1.8rem; }
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <nav class="col-md-3 col-lg-2 sidebar d-md-block">
                <div class="logo">
                    <h4>🏫 School</h4>
                    <small>Management System</small>
                </div>
                <ul class="nav flex-column">
                    <li class="nav-item">
                        <a class="nav-link {% if request.endpoint == 'dashboard' %}active{% endif %}" 
                           href="{{ url_for('dashboard') }}">
                            <i class="bi bi-speedometer2"></i> Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.endpoint in ['students', 'add_student', 'edit_student', 'view_student'] %}active{% endif %}" 
                           href="{{ url_for('students') }}">
                            <i class="bi bi-people"></i> Students
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.endpoint in ['teachers', 'add_teacher', 'edit_teacher'] %}active{% endif %}" 
                           href="{{ url_for('teachers') }}">
                            <i class="bi bi-person-badge"></i> Teachers
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.endpoint in ['classes', 'add_class', 'edit_class', 'view_class'] %}active{% endif %}" 
                           href="{{ url_for('classes') }}">
                            <i class="bi bi-book"></i> Classes
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if request.endpoint in ['subjects', 'add_subject'] %}active{% endif %}" 
                           href="{{ url_for('subjects') }}">
                            <i class="bi bi-journal"></i> Subjects
                        </a>
                    </li>
                    <li class="nav-item mt-4">
                        <a class="nav-link text-danger" href="{{ url_for('logout') }}">
                            <i class="bi bi-box-arrow-right"></i> Logout
                        </a>
                    </li>
                </ul>
            </nav>
            <main class="col-md-9 col-lg-10 main-content">
                <div class="top-bar">
                    <div>
                        <h2>{% block page_title %}Dashboard{% endblock %}</h2>
                        <span class="subtitle">{% block page_subtitle %}Welcome back!{% endblock %}</span>
                    </div>
                    <div class="user-info">
                        <div class="text-end">
                            <div class="name">{{ current_user.name }}</div>
                            <div class="role">{{ current_user.role }}</div>
                        </div>
                        <a href="{{ url_for('logout') }}" class="btn-logout">
                            <i class="bi bi-box-arrow-right"></i> Logout
                        </a>
                    </div>
                </div>
                {% with messages = get_flashed_messages(with_categories=true) %}
                    {% if messages %}
                        {% for category, message in messages %}
                            <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                                {{ message }}
                                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                            </div>
                        {% endfor %}
                    {% endif %}
                {% endwith %}
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
    ''',
    
    'dashboard.html': '''
{% extends "base.html" %}
{% block title %}Dashboard{% endblock %}
{% block page_title %}📊 Dashboard{% endblock %}
{% block page_subtitle %}Overview of your school management system{% endblock %}
{% block content %}
<div class="row g-4 mb-4">
    <div class="col-md-3">
        <div class="stat-card">
            <div class="number">{{ stats.students }}</div>
            <div class="label">👨‍🎓 Students</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card" style="border-top-color: #45b7d1;">
            <div class="number">{{ stats.teachers }}</div>
            <div class="label">👨‍🏫 Teachers</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card" style="border-top-color: #96ceb4;">
            <div class="number">{{ stats.classes }}</div>
            <div class="label">📚 Classes</div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="stat-card" style="border-top-color: #dda0dd;">
            <div class="number">{{ stats.subjects }}</div>
            <div class="label">📖 Subjects</div>
        </div>
    </div>
</div>
<div class="card">
    <h5 class="card-title">📋 Recent Activity</h5>
    <hr>
    <div class="text-muted">
        <p><i class="bi bi-check-circle text-success"></i> System started successfully</p>
        <p><i class="bi bi-people text-info"></i> Total Students: {{ stats.students }}</p>
        <p><i class="bi bi-person-badge text-info"></i> Total Teachers: {{ stats.teachers }}</p>
        <p><i class="bi bi-book text-info"></i> Total Classes: {{ stats.classes }}</p>
        <p><i class="bi bi-journal text-info"></i> Total Subjects: {{ stats.subjects }}</p>
        <p><i class="bi bi-calendar text-muted"></i> Today's Date: {{ now.strftime('%Y-%m-%d') }}</p>
        <p><i class="bi bi-clock text-muted"></i> Time: {{ now.strftime('%H:%M:%S') }}</p>
    </div>
</div>
<div class="card mt-4">
    <h5 class="card-title">👨‍🎓 Recent Students</h5>
    <hr>
    {% if stats.recent_students %}
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr><th>#</th><th>Name</th><th>Class</th><th>Parent</th><th>Action</th></tr>
                </thead>
                <tbody>
                    {% for student in stats.recent_students %}
                    <tr>
                        <td>{{ student.id }}</td>
                        <td>{{ student.name }}</td>
                        <td><span class="badge bg-info">{{ student.class_name }}</span></td>
                        <td>{{ student.parent_name }}</td>
                        <td>
                            <a href="{{ url_for('view_student', id=student.id) }}" 
                               class="btn btn-sm btn-primary">View</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% else %}
        <p class="text-muted">No students added yet.</p>
    {% endif %}
</div>
{% endblock %}
    ''',
    
    'students.html': '''
{% extends "base.html" %}
{% block title %}Students{% endblock %}
{% block page_title %}👨‍🎓 Student Management{% endblock %}
{% block page_subtitle %}Manage all students in the system{% endblock %}
{% block content %}
<div class="card">
    <div class="d-flex justify-content-between align-items-center">
        <span class="text-muted">Total: {{ students|length }}</span>
        <a href="{{ url_for('add_student') }}" class="btn btn-primary">
            <i class="bi bi-plus-circle"></i> Add Student
        </a>
    </div>
</div>
<div class="card mt-4">
    <div class="table-responsive">
        <table class="table">
            <thead>
                <tr><th>ID</th><th>Name</th><th>Class</th><th>Parent</th><th>Phone</th><th>Actions</th></tr>
            </thead>
            <tbody>
                {% if students %}
                    {% for student in students %}
                    <tr>
                        <td>{{ student.id }}</td>
                        <td><strong>{{ student.name }}</strong></td>
                        <td><span class="badge bg-info">{{ student.class_name }}</span></td>
                        <td>{{ student.parent_name }}</td>
                        <td>{{ student.phone }}</td>
                        <td>
                            <a href="{{ url_for('view_student', id=student.id) }}" 
                               class="btn btn-sm btn-primary">View</a>
                            <a href="{{ url_for('edit_student', id=student.id) }}" 
                               class="btn btn-sm btn-warning">Edit</a>
                            <a href="{{ url_for('delete_student', id=student.id) }}" 
                               class="btn btn-sm btn-danger" 
                               onclick="return confirm('Delete this student?')">Delete</a>
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr><td colspan="6" class="text-center text-muted py-4">
                        No students found. <a href="{{ url_for('add_student') }}">Add your first student!</a>
                    </td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
    ''',
    
    'student_form.html': '''
{% extends "base.html" %}
{% block title %}{{ title }}{% endblock %}
{% block page_title %}{{ title }}{% endblock %}
{% block page_subtitle %}{% if student %}Update student information{% else %}Add new student to the system{% endif %}{% endblock %}
{% block content %}
<div class="card">
    <form method="POST">
        <div class="row">
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="name" class="form-label">Full Name *</label>
                    <input type="text" class="form-control" id="name" name="name" 
                           value="{{ student.name if student else '' }}" required>
                </div>
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" name="email" 
                           value="{{ student.email if student else '' }}">
                </div>
                <div class="mb-3">
                    <label for="phone" class="form-label">Phone *</label>
                    <input type="text" class="form-control" id="phone" name="phone" 
                           value="{{ student.phone if student else '' }}" required>
                </div>
                <div class="mb-3">
                    <label for="address" class="form-label">Address</label>
                    <input type="text" class="form-control" id="address" name="address" 
                           value="{{ student.address if student else '' }}">
                </div>
            </div>
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="class_name" class="form-label">Class *</label>
                    <input type="text" class="form-control" id="class_name" name="class_name" 
                           value="{{ student.class_name if student else '' }}" required>
                </div>
                <div class="mb-3">
                    <label for="parent_name" class="form-label">Parent Name *</label>
                    <input type="text" class="form-control" id="parent_name" name="parent_name" 
                           value="{{ student.parent_name if student else '' }}" required>
                </div>
                <div class="mb-3">
                    <label for="parent_phone" class="form-label">Parent Phone *</label>
                    <input type="text" class="form-control" id="parent_phone" name="parent_phone" 
                           value="{{ student.parent_phone if student else '' }}" required>
                </div>
            </div>
        </div>
        <div class="d-flex gap-2 mt-3">
            <button type="submit" class="btn btn-primary"><i class="bi bi-save"></i> Save Student</button>
            <a href="{{ url_for('students') }}" class="btn btn-secondary">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}
    ''',
    
    'student_view.html': '''
{% extends "base.html" %}
{% block title %}Student Details{% endblock %}
{% block page_title %}👤 Student Details{% endblock %}
{% block page_subtitle %}Complete information about {{ student.name }}{% endblock %}
{% block content %}
<div class="card">
    <div class="row">
        <div class="col-md-6">
            <h5 class="text-muted">Personal Information</h5><hr>
            <p><strong>ID:</strong> {{ student.id }}</p>
            <p><strong>Name:</strong> {{ student.name }}</p>
            <p><strong>Email:</strong> {{ student.email or 'N/A' }}</p>
            <p><strong>Phone:</strong> {{ student.phone }}</p>
            <p><strong>Address:</strong> {{ student.address or 'N/A' }}</p>
        </div>
        <div class="col-md-6">
            <h5 class="text-muted">Academic Information</h5><hr>
            <p><strong>Class:</strong> {{ student.class_name }}</p>
            <p><strong>Parent Name:</strong> {{ student.parent_name }}</p>
            <p><strong>Parent Phone:</strong> {{ student.parent_phone }}</p>
            <p><strong>Enrollment Date:</strong> {{ student.enrollment_date.strftime('%Y-%m-%d') }}</p>
        </div>
    </div>
    <div class="d-flex gap-2 mt-3">
        <a href="{{ url_for('edit_student', id=student.id) }}" class="btn btn-warning">
            <i class="bi bi-pencil"></i> Edit
        </a>
        <a href="{{ url_for('students') }}" class="btn btn-secondary">
            <i class="bi bi-arrow-left"></i> Back to List
        </a>
    </div>
</div>
{% endblock %}
    ''',
    
    'teachers.html': '''
{% extends "base.html" %}
{% block title %}Teachers{% endblock %}
{% block page_title %}👨‍🏫 Teacher Management{% endblock %}
{% block page_subtitle %}Manage all teachers in the system{% endblock %}
{% block content %}
<div class="card">
    <div class="d-flex justify-content-between align-items-center">
        <span class="text-muted">Total: {{ teachers|length }}</span>
        <a href="{{ url_for('add_teacher') }}" class="btn btn-primary">
            <i class="bi bi-plus-circle"></i> Add Teacher
        </a>
    </div>
</div>
<div class="card mt-4">
    <div class="table-responsive">
        <table class="table">
            <thead>
                <tr><th>ID</th><th>Name</th><th>Qualification</th><th>Phone</th><th>Actions</th></tr>
            </thead>
            <tbody>
                {% if teachers %}
                    {% for teacher in teachers %}
                    <tr>
                        <td>{{ teacher.id }}</td>
                        <td><strong>{{ teacher.name }}</strong></td>
                        <td>{{ teacher.qualification }}</td>
                        <td>{{ teacher.phone }}</td>
                        <td>
                            <a href="{{ url_for('edit_teacher', id=teacher.id) }}" 
                               class="btn btn-sm btn-warning">Edit</a>
                            <a href="{{ url_for('delete_teacher', id=teacher.id) }}" 
                               class="btn btn-sm btn-danger" 
                               onclick="return confirm('Delete this teacher?')">Delete</a>
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr><td colspan="5" class="text-center text-muted py-4">
                        No teachers found. <a href="{{ url_for('add_teacher') }}">Add your first teacher!</a>
                    </td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
    ''',
    
    'teacher_form.html': '''
{% extends "base.html" %}
{% block title %}{{ title }}{% endblock %}
{% block page_title %}{{ title }}{% endblock %}
{% block page_subtitle %}{% if teacher %}Update teacher information{% else %}Add new teacher to the system{% endif %}{% endblock %}
{% block content %}
<div class="card">
    <form method="POST">
        <div class="row">
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="name" class="form-label">Full Name *</label>
                    <input type="text" class="form-control" id="name" name="name" 
                           value="{{ teacher.name if teacher else '' }}" required>
                </div>
                <div class="mb-3">
                    <label for="email" class="form-label">Email</label>
                    <input type="email" class="form-control" id="email" name="email" 
                           value="{{ teacher.email if teacher else '' }}">
                </div>
                <div class="mb-3">
                    <label for="phone" class="form-label">Phone *</label>
                    <input type="text" class="form-control" id="phone" name="phone" 
                           value="{{ teacher.phone if teacher else '' }}" required>
                </div>
            </div>
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="address" class="form-label">Address</label>
                    <input type="text" class="form-control" id="address" name="address" 
                           value="{{ teacher.address if teacher else '' }}">
                </div>
                <div class="mb-3">
                    <label for="qualification" class="form-label">Qualification *</label>
                    <input type="text" class="form-control" id="qualification" name="qualification" 
                           value="{{ teacher.qualification if teacher else '' }}" required>
                </div>
            </div>
        </div>
        <div class="d-flex gap-2 mt-3">
            <button type="submit" class="btn btn-primary"><i class="bi bi-save"></i> Save Teacher</button>
            <a href="{{ url_for('teachers') }}" class="btn btn-secondary">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}
    ''',
    
    'classes.html': '''
{% extends "base.html" %}
{% block title %}Classes{% endblock %}
{% block page_title %}📚 Class Management{% endblock %}
{% block page_subtitle %}Manage all classes in the system{% endblock %}
{% block content %}
<div class="card">
    <div class="d-flex justify-content-between align-items-center">
        <span class="text-muted">Total: {{ classes|length }}</span>
        <a href="{{ url_for('add_class') }}" class="btn btn-primary">
            <i class="bi bi-plus-circle"></i> Add Class
        </a>
    </div>
</div>
<div class="card mt-4">
    <div class="table-responsive">
        <table class="table">
            <thead>
                <tr><th>ID</th><th>Class Name</th><th>Section</th><th>Actions</th></tr>
            </thead>
            <tbody>
                {% if classes %}
                    {% for class_obj in classes %}
                    <tr>
                        <td>{{ class_obj.id }}</td>
                        <td><strong>{{ class_obj.name }}</strong></td>
                        <td>{{ class_obj.section or 'N/A' }}</td>
                        <td>
                            <a href="{{ url_for('view_class', id=class_obj.id) }}" 
                               class="btn btn-sm btn-primary">View</a>
                            <a href="{{ url_for('edit_class', id=class_obj.id) }}" 
                               class="btn btn-sm btn-warning">Edit</a>
                            <a href="{{ url_for('delete_class', id=class_obj.id) }}" 
                               class="btn btn-sm btn-danger" 
                               onclick="return confirm('Delete this class?')">Delete</a>
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr><td colspan="4" class="text-center text-muted py-4">
                        No classes found. <a href="{{ url_for('add_class') }}">Add your first class!</a>
                    </td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
    ''',
    
    'class_form.html': '''
{% extends "base.html" %}
{% block title %}{{ title }}{% endblock %}
{% block page_title %}{{ title }}{% endblock %}
{% block page_subtitle %}{% if class_obj %}Update class information{% else %}Add new class to the system{% endif %}{% endblock %}
{% block content %}
<div class="card">
    <form method="POST">
        <div class="row">
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="name" class="form-label">Class Name *</label>
                    <input type="text" class="form-control" id="name" name="name" 
                           value="{{ class_obj.name if class_obj else '' }}" required>
                </div>
            </div>
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="section" class="form-label">Section</label>
                    <input type="text" class="form-control" id="section" name="section" 
                           value="{{ class_obj.section if class_obj else '' }}">
                </div>
            </div>
        </div>
        <div class="d-flex gap-2 mt-3">
            <button type="submit" class="btn btn-primary"><i class="bi bi-save"></i> Save Class</button>
            <a href="{{ url_for('classes') }}" class="btn btn-secondary">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}
    ''',
    
    'class_view.html': '''
{% extends "base.html" %}
{% block title %}Class Details{% endblock %}
{% block page_title %}📚 Class Details{% endblock %}
{% block page_subtitle %}{{ class_obj.name }} - Section {{ class_obj.section or 'N/A' }}{% endblock %}
{% block content %}
<div class="card">
    <h5 class="card-title">Students in this class</h5><hr>
    {% if students %}
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr><th>ID</th><th>Name</th><th>Parent</th><th>Phone</th><th>Action</th></tr>
                </thead>
                <tbody>
                    {% for student in students %}
                    <tr>
                        <td>{{ student.id }}</td>
                        <td>{{ student.name }}</td>
                        <td>{{ student.parent_name }}</td>
                        <td>{{ student.phone }}</td>
                        <td>
                            <a href="{{ url_for('view_student', id=student.id) }}" 
                               class="btn btn-sm btn-primary">View</a>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% else %}
        <p class="text-muted">No students enrolled in this class.</p>
    {% endif %}
    <div class="d-flex gap-2 mt-3">
        <a href="{{ url_for('classes') }}" class="btn btn-secondary">
            <i class="bi bi-arrow-left"></i> Back to Classes
        </a>
    </div>
</div>
{% endblock %}
    ''',
    
    'subjects.html': '''
{% extends "base.html" %}
{% block title %}Subjects{% endblock %}
{% block page_title %}📖 Subject Management{% endblock %}
{% block page_subtitle %}Manage all subjects in the system{% endblock %}
{% block content %}
<div class="card">
    <div class="d-flex justify-content-between align-items-center">
        <span class="text-muted">Total: {{ subjects|length }}</span>
        <a href="{{ url_for('add_subject') }}" class="btn btn-primary">
            <i class="bi bi-plus-circle"></i> Add Subject
        </a>
    </div>
</div>
<div class="card mt-4">
    <div class="table-responsive">
        <table class="table">
            <thead>
                <tr><th>ID</th><th>Subject Name</th><th>Code</th><th>Description</th><th>Actions</th></tr>
            </thead>
            <tbody>
                {% if subjects %}
                    {% for subject in subjects %}
                    <tr>
                        <td>{{ subject.id }}</td>
                        <td><strong>{{ subject.name }}</strong></td>
                        <td>{{ subject.code or '-' }}</td>
                        <td>{{ subject.description or '-' }}</td>
                        <td>
                            <a href="{{ url_for('delete_subject', id=subject.id) }}" 
                               class="btn btn-sm btn-danger" 
                               onclick="return confirm('Delete this subject?')">Delete</a>
                        </td>
                    </tr>
                    {% endfor %}
                {% else %}
                    <tr><td colspan="5" class="text-center text-muted py-4">
                        No subjects found. <a href="{{ url_for('add_subject') }}">Add your first subject!</a>
                    </td></tr>
                {% endif %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
    ''',
    
    'subject_form.html': '''
{% extends "base.html" %}
{% block title %}{{ title }}{% endblock %}
{% block page_title %}{{ title }}{% endblock %}
{% block page_subtitle %}{% if subject %}Update subject information{% else %}Add new subject to the system{% endif %}{% endblock %}
{% block content %}
<div class="card">
    <form method="POST">
        <div class="row">
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="name" class="form-label">Subject Name *</label>
                    <input type="text" class="form-control" id="name" name="name" 
                           value="{{ subject.name if subject else '' }}" required>
                </div>
            </div>
            <div class="col-md-6">
                <div class="mb-3">
                    <label for="code" class="form-label">Subject Code</label>
                    <input type="text" class="form-control" id="code" name="code" 
                           value="{{ subject.code if subject else '' }}">
                </div>
            </div>
        </div>
        <div class="mb-3">
            <label for="description" class="form-label">Description</label>
            <input type="text" class="form-control" id="description" name="description" 
                   value="{{ subject.description if subject else '' }}">
        </div>
        <div class="d-flex gap-2 mt-3">
            <button type="submit" class="btn btn-primary"><i class="bi bi-save"></i> Save Subject</button>
            <a href="{{ url_for('subjects') }}" class="btn btn-secondary">Cancel</a>
        </div>
    </form>
</div>
{% endblock %}
    '''
}

# ========================================================
# CUSTOM TEMPLATE LOADER
# ========================================================

from jinja2 import Environment, BaseLoader, TemplateNotFound

class StringTemplateLoader(BaseLoader):
    def __init__(self, templates):
        self.templates = templates

    def get_source(self, environment, template):
        if template in self.templates:
            return self.templates[template], None, lambda: True
        raise TemplateNotFound(template)

# Replace Flask's template loader with our string loader
app.jinja_loader = StringTemplateLoader(TEMPLATES)

# ========================================================
# ROUTES - AUTHENTICATION
# ========================================================

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Login successful! Welcome back.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ========================================================
# ROUTES - DASHBOARD
# ========================================================

@app.route('/dashboard')
@login_required
def dashboard():
    stats = {
        'students': Student.query.count(),
        'teachers': Teacher.query.count(),
        'classes': Class.query.count(),
        'subjects': Subject.query.count(),
        'recent_students': Student.query.order_by(Student.id.desc()).limit(5).all()
    }
    return render_template('dashboard.html', stats=stats, now=datetime.now())

# ========================================================
# ROUTES - STUDENTS
# ========================================================

@app.route('/students')
@login_required
def students():
    return render_template('students.html', students=Student.query.order_by(Student.id.desc()).all())

@app.route('/students/add', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        student = Student(
            name=request.form.get('name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            class_name=request.form.get('class_name'),
            parent_name=request.form.get('parent_name'),
            parent_phone=request.form.get('parent_phone')
        )
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('students'))
    return render_template('student_form.html', title='Add Student', student=None)

@app.route('/students/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.name = request.form.get('name')
        student.email = request.form.get('email')
        student.phone = request.form.get('phone')
        student.address = request.form.get('address')
        student.class_name = request.form.get('class_name')
        student.parent_name = request.form.get('parent_name')
        student.parent_phone = request.form.get('parent_phone')
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('students'))
    return render_template('student_form.html', title='Edit Student', student=student)

@app.route('/students/delete/<int:id>')
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('students'))

@app.route('/students/view/<int:id>')
@login_required
def view_student(id):
    return render_template('student_view.html', student=Student.query.get_or_404(id))

# ========================================================
# ROUTES - TEACHERS
# ========================================================

@app.route('/teachers')
@login_required
def teachers():
    return render_template('teachers.html', teachers=Teacher.query.order_by(Teacher.id.desc()).all())

@app.route('/teachers/add', methods=['GET', 'POST'])
@login_required
def add_teacher():
    if request.method == 'POST':
        teacher = Teacher(
            name=request.form.get('name'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            address=request.form.get('address'),
            qualification=request.form.get('qualification')
        )
        db.session.add(teacher)
        db.session.commit()
        flash('Teacher added successfully!', 'success')
        return redirect(url_for('teachers'))
    return render_template('teacher_form.html', title='Add Teacher', teacher=None)

@app.route('/teachers/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    if request.method == 'POST':
        teacher.name = request.form.get('name')
        teacher.email = request.form.get('email')
        teacher.phone = request.form.get('phone')
        teacher.address = request.form.get('address')
        teacher.qualification = request.form.get('qualification')
        db.session.commit()
        flash('Teacher updated successfully!', 'success')
        return redirect(url_for('teachers'))
    return render_template('teacher_form.html', title='Edit Teacher', teacher=teacher)

@app.route('/teachers/delete/<int:id>')
@login_required
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    flash('Teacher deleted successfully!', 'success')
    return redirect(url_for('teachers'))

# ========================================================
# ROUTES - CLASSES
# ========================================================

@app.route('/classes')
@login_required
def classes():
    return render_template('classes.html', classes=Class.query.order_by(Class.id.desc()).all())

@app.route('/classes/add', methods=['GET', 'POST'])
@login_required
def add_class():
    if request.method == 'POST':
        class_obj = Class(
            name=request.form.get('name'),
            section=request.form.get('section')
        )
        db.session.add(class_obj)
        db.session.commit()
        flash('Class added successfully!', 'success')
        return redirect(url_for('classes'))
    return render_template('class_form.html', title='Add Class', class_obj=None)

@app.route('/classes/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_class(id):
    class_obj = Class.query.get_or_404(id)
    if request.method == 'POST':
        class_obj.name = request.form.get('name')
        class_obj.section = request.form.get('section')
        db.session.commit()
        flash('Class updated successfully!', 'success')
        return redirect(url_for('classes'))
    return render_template('class_form.html', title='Edit Class', class_obj=class_obj)

@app.route('/classes/delete/<int:id>')
@login_required
def delete_class(id):
    class_obj = Class.query.get_or_404(id)
    db.session.delete(class_obj)
    db.session.commit()
    flash('Class deleted successfully!', 'success')
    return redirect(url_for('classes'))

@app.route('/classes/view/<int:id>')
@login_required
def view_class(id):
    class_obj = Class.query.get_or_404(id)
    students = Student.query.filter_by(class_name=class_obj.name).all()
    return render_template('class_view.html', class_obj=class_obj, students=students)

# ========================================================
# ROUTES - SUBJECTS
# ========================================================

@app.route('/subjects')
@login_required
def subjects():
    return render_template('subjects.html', subjects=Subject.query.order_by(Subject.id.desc()).all())

@app.route('/subjects/add', methods=['GET', 'POST'])
@login_required
def add_subject():
    if request.method == 'POST':
        name = request.form.get('name')
        if Subject.query.filter_by(name=name).first():
            flash('Subject already exists!', 'warning')
            return redirect(url_for('subjects'))
        
        subject = Subject(
            name=name,
            code=request.form.get('code'),
            description=request.form.get('description')
        )
        db.session.add(subject)
        db.session.commit()
        flash('Subject added successfully!', 'success')
        return redirect(url_for('subjects'))
    return render_template('subject_form.html', title='Add Subject', subject=None)

@app.route('/subjects/delete/<int:id>')
@login_required
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    db.session.delete(subject)
    db.session.commit()
    flash('Subject deleted successfully!', 'success')
    return redirect(url_for('subjects'))

# ========================================================
# INITIALIZE DATABASE
# ========================================================

def init_db():
    with app.app_context():
        db.create_all()
        
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', name='System Admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('✅ Admin user created: admin / admin123')
        
        if Student.query.count() == 0:
            sample_students = [
                ('Ali Ahmed', 'ali@email.com', '03001234567', 'Karachi', 'Class 1', 'Mr. Ahmed', '03001234568'),
                ('Sara Khan', 'sara@email.com', '03012345678', 'Lahore', 'Class 1', 'Mr. Khan', '03012345679'),
                ('Usman Malik', 'usman@email.com', '03023456789', 'Islamabad', 'Class 2', 'Mr. Malik', '03023456780'),
            ]
            for s in sample_students:
                db.session.add(Student(name=s[0], email=s[1], phone=s[2], address=s[3],
                                     class_name=s[4], parent_name=s[5], parent_phone=s[6]))
            
            sample_teachers = [
                ('Dr. Shahid', 'shahid@email.com', '03034567890', 'Karachi', 'PhD Mathematics'),
                ('Ms. Fatima', 'fatima@email.com', '03045678901', 'Lahore', 'MSc English'),
            ]
            for t in sample_teachers:
                db.session.add(Teacher(name=t[0], email=t[1], phone=t[2], address=t[3], qualification=t[4]))
            
            sample_classes = [('Class 1', 'A'), ('Class 2', 'B'), ('Class 3', 'A')]
            for c in sample_classes:
                db.session.add(Class(name=c[0], section=c[1]))
            
            for sub in ['Mathematics', 'English', 'Science', 'Urdu', 'Islamiat']:
                db.session.add(Subject(name=sub))
            
            db.session.commit()
            print('✅ Sample data created!')
        
        print('✅ Database initialized successfully!')

# ========================================================
# RUN APPLICATION
# ========================================================

if __name__ == '__main__':
    init_db()
    print("""
    🚀 School Management System is running!
    🌐 Open: http://localhost:5000
    🔑 Login: admin / admin123
    """)
    app.run(debug=True, host='0.0.0.0', port=5000)