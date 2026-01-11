# 🏠 Smart Room Automation – Secure IoT Web Application

Smart Room Automation is a secure IoT based web application designed to monitor environmental sensor data and allow authorised users to control room devices such as lighting in real time. The system integrates IoT hardware, a Flask backend, a relational database, and PubNub’s real time messaging infrastructure to provide secure, role based device interaction.

🌐 **Live Website:** https://www.autosmart.live

---

## 🚀 Key Features

- Real time sensor monitoring (motion, light, temperature, humidity)
- Remote light control via web dashboard and physical button
- Role based access control (Admin / User)
- Google Login
- Subscription based device control
- PubNub Access Manager with time limited tokens
- Audit logging for security and accountability
- Admin dashboard with CSV export
- Secure cloud deployment with HTTPS

---

## 🏗 System Architecture

The system follows a client server IoT architecture:

- **Web Browser** – User interface for dashboard and admin tools  
- **Flask Backend** – Authentication, authorization, database access  
- **MariaDB** – Stores users, sensor logs, audit logs, and subscriptions  
- **PubNub** – Secure real time messaging between system components  
- **Raspberry Pi** – Publishes sensor data and listens for control commands  

All communication is secured using PubNub Access Manager tokens and server-side permission checks.

---

## 🔐 Security Overview

- Password hashing with Werkzeug
- Session-based authentication (Flask-Login)
- Role and subscription based route protection
- PubNub Access Manager with scoped, expiring tokens
- HTTPS encryption using Let’s Encrypt
- Encrypted PubNub channels (TLS)
- Audit logging of sensitive actions
- Database credentials stored securely in `.env`

---

## 🛠 Hardware Used

- Raspberry Pi  
- PIR Motion Sensor  
- LDR Light Sensor  
- DHT Temperature & Humidity Sensor  
- Relay Module  
- Ultra Bright LED  
- Physical Push Button  
- Resistors  

---

## ☁️ Deployment

- **Cloud Provider:** AWS EC2 (Ubuntu)
- **Web Server:** Apache + mod_wsgi
- **Database:** MariaDB
- **Domain:** autosmart.live
- **SSL:** Let’s Encrypt (HTTPS enforced)

---

## 👤 Author

**Eyob Gebrekidan**
