# Simple Cloud App
Demonstration: https://www.youtube.com/watch?v=cr3Dny0Kma0 
A simple Python/Flask web application deployed on AWS EC2 using Kubernetes (k3s) and Docker. Supports full CRUD operations on messages, backed by a SQLite database persisted via a Kubernetes PersistentVolumeClaim.

---

## Features

- Add, edit, and delete messages stored in SQLite
- Live monitoring dashboard (`/stats`) showing pod identity, DB stats, and HPA config
- Health check endpoint (`/health`) used as a Kubernetes liveness probe
- Nginx reverse proxy in front of Flask/Gunicorn
- Horizontal Pod Autoscaler (scales 2–5 replicas based on CPU)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask, Gunicorn |
| Database | SQLite (PersistentVolumeClaim) |
| Containerisation | Docker |
| Orchestration | Kubernetes (k3s) |
| Reverse Proxy | Nginx |
| Cloud | AWS EC2 |

---

## Project Structure

```
├── app.py                   # Flask application
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Local development setup
├── nginx/
│   └── nginx.conf           # Nginx reverse proxy config
└── k8s/
    ├── flask-deployment.yaml
    ├── flask-service.yaml
    ├── flask-pvc.yaml
    ├── flask-hpa.yaml
    ├── nginx-deployment.yaml
    ├── nginx-service.yaml
    └── nginx-configmap.yaml
```

---

## Running Locally (Docker Compose)

```bash
docker-compose up --build
```

Then open [http://localhost](http://localhost).

---

## Deploying to Kubernetes

```bash
kubectl apply -f k8s/
```

The app will be available on port `30080` of your node:

```
http://<your-node-ip>:30080
```

---

## Endpoints

| Route | Description |
|---|---|
| `/` | Main app — add, edit, delete messages |
| `/stats` | Live monitor — pod info, DB stats, cluster config |
| `/health` | Health check (JSON or HTML) |

---

## Kubernetes Architecture

The HPA scales Flask pods between **2 and 5 replicas** when average CPU utilisation exceeds **50%**.
