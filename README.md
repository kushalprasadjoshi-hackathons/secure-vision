# 🔒 Secure Vision

<div align="center">

![Secure Vision Logo](https://img.shields.io/badge/Secure-Vision-blue?style=for-the-badge&logo=security&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.3.3-lightgrey?style=flat-square&logo=flask)
![OpenCV](https://img.shields.io/badge/OpenCV-4.13+-red?style=flat-square&logo=opencv)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**AI-Powered Smart Surveillance System with Real-Time Face Recognition**

[📖 Documentation](#-documentation) • [🚀 Quick Start](#-quick-start) • [📊 Features](#-features) • [🛠️ Installation](#-installation)

</div>

---

## 📋 Table of Contents

- [🔒 Secure Vision](#-secure-vision)
  - [📋 Table of Contents](#-table-of-contents)
  - [📖 Overview](#-overview)
  - [✨ Features](#-features)
  - [🏗️ Architecture](#️-architecture)
  - [🛠️ Installation](#️-installation)
  - [🚀 Quick Start](#-quick-start)
  - [📖 Usage Guide](#-usage-guide)
  - [⚙️ Configuration](#️-configuration)
  - [📊 Performance](#-performance)
  - [🖼️ Screenshots](#️-screenshots)
  - [🔮 Future Scope](#-future-scope)
  - [🤝 Contributing](#-contributing)
  - [📝 License](#-license)
  - [🙏 Acknowledgments](#-acknowledgments)

---

## 📖 Overview

**Secure Vision** is an advanced AI-powered surveillance system that provides real-time video monitoring with intelligent face detection, recognition, and automated alerting capabilities. Built with cutting-edge computer vision technologies, it offers a comprehensive security solution for homes, businesses, and organizations.

The system leverages state-of-the-art machine learning algorithms to identify known individuals, detect unknown persons, and trigger appropriate security responses. With its web-based interface and optimized performance, Secure Vision delivers enterprise-grade surveillance capabilities with ease of use.

---

## ✨ Features

### 🔍 **Core Surveillance Features**
- **Real-Time Video Streaming** - Live camera feed with low-latency processing
- **Face Detection** - Advanced Haar Cascade-based face detection
- **Face Recognition** - AI-powered facial recognition with high accuracy
- **Motion Detection** - Background subtraction for movement tracking
- **Multi-Camera Support** - Extensible architecture for multiple cameras

### 🚨 **Alert & Notification System**
- **Email Alerts** - SMTP-based email notifications with snapshot attachments
- **Configurable Recipients** - Multiple alert channels and recipients
- **Smart Alert Filtering** - Cooldown periods to prevent alert spam
- **Event Logging** - Comprehensive logging of all security events

### ⚡ **Performance & Optimization**
- **Real-Time Processing** - Optimized for 15-30 FPS performance
- **Memory Management** - Automatic cleanup and resource optimization
- **CPU Optimization** - Intelligent frame skipping and batch processing
- **Caching System** - LRU cache for face recognition results

### 🌐 **User Interface**
- **Web Dashboard** - Intuitive web interface for system control
- **Live Monitoring** - Real-time video feed with overlay annotations
- **System Status** - Performance metrics and system health monitoring
- **Configuration Panel** - Easy-to-use settings management

### 🔧 **Developer Features**
- **RESTful API** - Programmatic access to all system functions
- **Modular Architecture** - Clean separation of concerns
- **Extensible Design** - Easy to add new detection algorithms
- **Comprehensive Testing** - Automated test suite for reliability

---

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Interface │    │   Flask Server  │    │   Surveillance  │
│   (HTML/CSS/JS) │◄──►│   (REST API)    │◄──►│   Engine        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Video Stream  │    │   Face Database │    │   Alert System  │
│   (MJPEG)       │    │   (SQLite)      │    │   (Email/SMS)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### **System Components**

#### **Frontend Layer**
- **Web Interface**: Responsive dashboard built with HTML5, CSS3, and JavaScript
- **Real-Time Streaming**: MJPEG video feed with overlay annotations
- **Control Panel**: System configuration and monitoring interface

#### **Backend Layer**
- **Flask Application**: RESTful API server with WebSocket support
- **Camera Manager**: Multi-threaded camera capture and processing
- **Detection Engine**: Computer vision pipeline with optimized algorithms

#### **Data Layer**
- **Face Database**: SQLite storage for known face encodings
- **Event Logs**: Comprehensive logging system with retention policies
- **Configuration**: Centralized settings management

#### **Integration Layer**
- **Alert System**: Email/SMS notifications with attachment support
- **Performance Monitor**: Real-time metrics and health checks
- **API Endpoints**: Programmatic access for third-party integrations

---

## 🛠️ Installation

### **Prerequisites**

- **Python 3.8+**
- **Camera/Webcam** (built-in or external)
- **Internet Connection** (for email alerts)
- **4GB RAM** (recommended)
- **Modern Web Browser** (Chrome, Firefox, Safari, Edge)

### **Step-by-Step Installation**

#### 1. **Clone the Repository**
```bash
git clone https://github.com/kushalprasadjoshi-hackathons/secure-vision.git
cd secure-vision
```

#### 2. **Create Virtual Environment**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

#### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

#### 4. **Optional: Install Face Recognition**
```bash
# For full face recognition capabilities
pip install dlib face-recognition
```

#### 5. **Configure the System**
```bash
# Edit config.py with your settings
# Configure camera index, email settings, etc.
```

#### 6. **Run Tests**
```bash
python test_system.py
```

---

## 🚀 Quick Start

### **Basic Setup (5 minutes)**

1. **Start the Application**
```bash
python app.py
```

2. **Open Web Interface**
```
http://localhost:5000
```

3. **Enable Surveillance**
- Click "Start Surveillance" in the web interface
- Grant camera permissions when prompted

4. **Add Known Faces** (Optional)
```bash
python setup_faces.py
```

### **Email Alerts Setup**

1. **Enable Email Alerts in `config.py`**
```python
ENABLE_EMAIL_ALERTS = True
SENDER_EMAIL = 'your-email@gmail.com'
SENDER_PASSWORD = 'your-app-password'
ALERT_RECIPIENT_EMAIL = 'admin@example.com'
```

2. **Test Email Configuration**
```bash
python -c "from surveillance.alert import Alert; Alert()._send_basic_email_alert('Test', 'Hello World')"
```

---

## 📖 Usage Guide

### **Web Interface**

#### **Dashboard Overview**
- **Live Video Feed**: Real-time camera stream with detection overlays
- **Control Panel**: Start/stop surveillance and adjust settings
- **Status Indicators**: System health and performance metrics
- **Event Log**: Recent security events and alerts

#### **Detection Settings**
- **Face Detection**: Toggle face detection on/off
- **Face Recognition**: Enable/disable facial recognition
- **Motion Detection**: Background motion tracking
- **Eye Detection**: Optional eye detection within faces

### **API Usage**

#### **Get System Status**
```bash
curl http://localhost:5000/camera_status
```

#### **Performance Metrics**
```bash
curl http://localhost:5000/performance_stats
```

#### **Start Surveillance**
```bash
curl -X POST http://localhost:5000/start_surveillance
```

### **Command Line Tools**

#### **Face Setup**
```bash
# Add known faces to the system
python setup_faces.py
```

#### **System Testing**
```bash
# Run comprehensive system tests
python test_system.py
```

#### **Development Server**
```bash
# Start with debug mode
FLASK_ENV=development python app.py
```

---

## ⚙️ Configuration

### **Core Settings** (`config.py`)

```python
# Application Settings
SECRET_KEY = 'your-secret-key'
DEBUG = False
DATABASE_URI = 'sqlite:///data/logs.db'

# Camera Configuration
CAMERA_INDEX = 0  # Default camera device
MAX_FRAME_RATE = 15  # Processing FPS limit

# Face Recognition
FACE_RECOGNITION_TOLERANCE = 0.6
KNOWN_FACES_DIR = 'data/known_faces'

# Alert System
ENABLE_EMAIL_ALERTS = False
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'your-email@gmail.com'
ALERT_RECIPIENT_EMAIL = 'admin@example.com'

# Performance Tuning
FRAME_SKIP_FACTOR = 2
FACE_RECOGNITION_BATCH_SIZE = 5
ENABLE_FACE_CACHE = True
```

### **Environment Variables**

For production deployment, use environment variables:

```bash
export SECRET_KEY='your-production-secret'
export ALERT_EMAIL='production-email@example.com'
export ALERT_EMAIL_PASSWORD='production-password'
```

### **Advanced Configuration**

- **Database**: Configure SQLite path or switch to PostgreSQL
- **Logging**: Adjust log levels and retention policies
- **Security**: Configure HTTPS and authentication
- **Performance**: Tune detection parameters for your hardware

---

## 📊 Performance

### **System Requirements**

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2.5 GHz Dual-Core | 3.0 GHz Quad-Core |
| **RAM** | 4 GB | 8 GB |
| **Storage** | 500 MB | 2 GB |
| **Camera** | 640x480 | 1280x720 HD |

### **Performance Metrics**

- **Face Detection**: 20-30 FPS
- **Face Recognition**: 5-15 FPS (with caching)
- **Memory Usage**: 200-400 MB
- **CPU Usage**: 30-60% during active detection
- **Latency**: <100ms frame processing

### **Optimization Features**

- **Frame Rate Limiting**: Prevents excessive CPU usage
- **Intelligent Caching**: LRU cache for recognition results
- **Memory Management**: Automatic cleanup and GC
- **Batch Processing**: Optimized for multiple faces
- **Threading**: Non-blocking camera capture

---

## 🔮 Future Scope

### **Short Term (3-6 months)**
- [ ] **Mobile App**: React Native mobile application
- [ ] **Cloud Storage**: AWS S3 integration for snapshots
- [ ] **Multi-Camera Support**: Dashboard for multiple cameras
- [ ] **Advanced Analytics**: Person tracking and behavior analysis

### **Medium Term (6-12 months)**
- [ ] **AI Integration**: Deep learning models for better accuracy
- [ ] **IoT Integration**: Smart home device integration
- [ ] **API Enhancements**: GraphQL API for better queries
- [ ] **Real-Time Alerts**: WebSocket push notifications

### **Long Term (1-2 years)**
- [ ] **Edge Computing**: Raspberry Pi and edge device support
- [ ] **Distributed System**: Multi-node surveillance network
- [ ] **Machine Learning**: Custom model training capabilities
- [ ] **Enterprise Features**: User management and role-based access

### **Research Areas**
- **Emotion Recognition**: Facial expression analysis
- **Crowd Analysis**: People counting and density monitoring
- **Anomaly Detection**: Unusual behavior identification
- **Privacy Protection**: Automatic face blurring for privacy

---

## 🤝 Contributing

We welcome contributions from the community! 

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenCV**: Computer vision library that powers our detection algorithms
- **Face Recognition**: Dlib-based facial recognition library
- **Flask**: Lightweight web framework for our API
- **NumPy**: Fundamental package for scientific computing
- **Python Community**: For the amazing ecosystem and tools

### **Inspiration**
This project was inspired by the growing need for accessible, AI-powered security solutions that balance effectiveness with privacy and ease of use.

---

<div align="center">

**Made with ❤️ for a safer world**

[⭐ Star us on GitHub](https://github.com/kushalprasadjoshi-hackathons/secure-vision) • [🐛 Report Issues](https://github.com/kushalprasadjoshi-hackathons/secure-vision/issues)

</div>