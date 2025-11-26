# **CalTrackAI**

### *Automated Nutrition Tracking from Photos*

CalTrackAI is an end-to-end AI system that predicts food items from images using a deep learning model (ResNet50 trained on Food-101), retrieves nutritional information, and provides interactive visualizations. The system includes:

* **Food recognition API (Flask)**
* **Nutrition estimation**
* **Monitoring with Prometheus + Grafana**
* **Frontend using Streamlit**
* **Dockerized multi-container deployment**
* **User feedback collection**
* **Drift & performance monitoring metrics**

This repository demonstrates the **full lifecycle of an AI system**—from model serving and data integrations to deployment, monitoring, and user interaction.

---
```
# 📁 **Repository Structure**
│   ├── README.md             # Main project documentation
│   ├── Risk Management and Trustworthiness.pdf  
│   └── AI System Project Proposal Template
│
├── 📁 monitoring
│   ├── 📁 grafana-data       # Grafana dashboards & persistent volume data
│   └── prometheus.yml        # Prometheus scrape configuration (backend metrics endpoint)
│
│── 📁 Risk_Management_Strategies
|    └── risk_management.ipynb   # Trustworthiness analysis notebook
|
|
├── 📁 src
│   ├── main.py                       # System launcher (runs docker-compose programmatically)
│   │
│   ├── 📁 backend
│   │   ├── app.py                    # Flask API (inference + USDA fuzzy match + Prometheus metrics)
│   │   ├── requirements.txt          # Backend Python dependencies
│   │   │
│   │   ├── 📁 data
│   │   │   ├── label_map.json        # Label-to-class mapping for trained model
│   │   │   ├── usda_food_data.csv    # Final 101-item USDA nutrition database
│   │   │   ├── feedback.jsonl        # Stores user feedback submitted from the frontend UI  
│   │   │   └── 📁 testing_images     # Sample images for quick inference testing
│   │   │
│   │   ├── 📁 model
│   │   │   └── resnet50_food101_final.keras   # Trained Food-101 model
│   │   ├── 📁 training-test
│   │   │   ├── 📁 notebooks
│   |   |         ├── 📁 Experiments/       
│   │   |         |   ├── EfficientNetB0.ipynb
│   │   |         |   ├── EfficientNetB3.ipynb
│   │   |         |   ├── experimental_model.ipynb
│   │   |         |   ├── MobileNetV2.ipynb
│   │   |         |   └── model1(poor accuracy).ipynb
│   │   |         |
│   |   |         ├── api_integration.ipynb        # Final USDA API pipeline & CSV generation
│   |   |         ├── data_preparation.ipynb       # Cleaning, preprocessing & dataset preparation
│   |   |         ├── ResNet50.ipynb               # Training notebook for final ResNet50 model
│   |   |         ├── ResNet50_Testing.ipynb       # Testing & evaluation notebook
│   │   └── 📁 uploads
│   │       └── (temp inference images auto-deleted after prediction)
│   │
│   ├── 📁 frontend
│       ├── app.py                    # Streamlit interface for predictions, charts & feedback
│       └── requirements.txt          # Frontend Python dependencies
│
├── 📁 Other_Trained_Models                  # trained models and experiment outputs
│
├── 📁 videos
│   └── CalTrackAI_Demo.mov           # Full deployment + monitoring demonstration video
│
├── .env                              # API keys & sensitive configs (not committed to GitHub)
├── .gitignore                        # Files to ignore in version control
└── requirements.txt                  # Global environment dependencies

```
---

# **How to Run the Entire System**

You can run the system in two ways:

## **Option A — Use the main.py Launcher**

``` bash
python src/main.py
```
This script:

* Builds all Docker containers

* Runs the full stack:

* Backend API

* Frontend Streamlit UI

* Prometheus

* Grafana



---

## **Option B — Run Manually**

```bash
docker-compose -f deployment/docker-compose.yml build
docker-compose -f deployment/docker-compose.yml up
```

---

# **System Components**

---

# **Backend (Flask API)**

Located in: `src/backend/app.py`

### Responsibilities:

* Loads trained **ResNet50 Food-101 model**
* Preprocesses images → runs inference
* Returns:

  * Top-1 prediction
  * Top-5 predictions
  * Nutrition (from USDA database)
* Fuzzy matching using **RapidFuzz**
* Logs metrics to **Prometheus**
* Accepts and stores user feedback → `feedback_log.json`

API endpoints:

| Endpoint    | Description                   |
| ----------- | ----------------------------- |
| `/predict`  | Run inference + get nutrition |
| `/feedback` | Store user feedback           |
| `/metrics`  | Prometheus metrics            |

Backend runs at
📍 **[http://localhost:3000](http://localhost:3000)**

---

# **Frontend (Streamlit)**

Located: `src/frontend/app.py`

### Features:

* Upload food images
* Displays:

  * Top-1 prediction
  * Confidence bar
  * Top-5 predictions table
  * Nutrition table (100g basis)
  * Slider to scale serving size
  * Pie chart for macro breakdown
* Feedback interaction (👍 / 👎 + comment input)

Frontend runs at
📍 **[http://localhost:8501](http://localhost:8501)**

---

## Video Demonstration

Below is the full demonstration of the CalTrackAI system showing:

- Frontend food recognition interface  
- Backend inference workflow  
- USDA nutrition retrieval  
- Prometheus metrics collection  
- Grafana dashboards  
- Dockerized deployment  

**Click below to watch the demo:**

[![Demo Video](videos/demo_thumbnail.png)](videos/CalTrackAI_Demo.mov)

---

# **Deployment Strategy (Docker + Prometheus + Grafana)**

**Tooling Used:**

* Docker (containerization)
* Docker Compose (multi-container orchestration)
* Prometheus + Grafana (monitoring)

CalTrackAI uses a multi-container production-ready setup:

Flask Backend serves predictions

Streamlit Frontend for user interaction

Prometheus scrapes model metrics (latency, confidence, request count)

Grafana visualizes system performance in dashboards

All deployment components live under:

```
deployment/
monitoring/
src/backend/
src/frontend/
```

### Why Docker?

* Ensures consistent environment
* Scalable
* Portable
* Simulates real-world deployment stacks

---

# **Monitoring (Prometheus + Grafana)**

Prometheus scrapes metrics from backend (`/metrics`):

### Metrics collected:

| Metric Name                  | Description                   |
| ---------------------------- | ----------------------------- |
| `prediction_requests_total`  | Total number of API calls     |
| `prediction_errors_total`    | Failed API requests           |
| `prediction_latency_seconds` | Model inference latency       |
| `prediction_confidence`      | Histogram of model confidence |
| `feedback_yes_total`         | No.of positive feedbacks      |
| `feedback_no_total`          | No.of negative feedbacks      |

---

## 📍 Prometheus

Runs at: **[http://localhost:9090](http://localhost:9090)**

---

## 📍 Grafana

Runs at: **[http://localhost:3001](http://localhost:3001)**

Use Prometheus as the data source and configure dashboards to visualize:

* API latency
* Request volume
* Error rates
* Model confidence drift


---

# **Security Measures Implemented**
```
src/backend/feedback_log.json
```

Used to:

* Identify incorrect predictions
* Improve nutrition fuzzy matching
* Monitor user satisfaction trends

---

# **Requirements Installation (Local, Without Docker)**

### Backend:

```bash
pip install -r src/backend/requirements.txt
python src/backend/app.py
```

### Frontend:

```bash
pip install -r src/frontend/requirements.txt
streamlit run src/frontend/app.py
```

---

# **Project Documentation**

Located inside:

```
documentation/
```

Includes:

* AI System Proposal Template
* Final Project Report (business/research style)
* This README

---

# **Version Control & Collaboration**

The repository follows:

* Feature-based branching (feature/frontend-ui, feature-prometheus)

* Pull requests for every major update

* Commit messages aligned with conventional standards

* .gitignore to keep the repo clean from generated artifacts

---

# **Acknowledgements**

This project is part of the **AI Systems** coursework, demonstrating full-stack MLOps concepts including deployment, monitoring, and model serving.

---
