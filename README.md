# Flask To-Do App: CI/CD with Jenkins, Docker and AWS EC2

A small Flask to-do app whose main purpose is to show a complete CI/CD pipeline.
Every `git push` to GitHub triggers Jenkins, which tests the code, builds a Docker
image, deploys it to an AWS EC2 instance, and verifies the deployment is healthy.

## Pipeline

```
GitHub push -> Webhook -> Jenkins
                            |-- 1. Checkout
                            |-- 2. Test         (pytest inside Docker build)
                            |-- 3. Build Image  (multi-stage, non-root, healthcheck)
                            |-- 4. Deploy       (docker run on EC2)
                            '-- 5. Smoke Test   (curl /health)
```

## Tech stack

Python 3.12, Flask, Gunicorn, pytest, Docker (multi-stage build), Jenkins (declarative pipeline), AWS EC2, GitHub webhooks.

## Project structure

```
.
├── app/
│   ├── __init__.py        # Flask app factory + routes
│   └── templates/index.html
├── tests/test_app.py      # pytest tests
├── wsgi.py                # Gunicorn entry point
├── Dockerfile             # test stage + runtime stage
├── Jenkinsfile            # pipeline definition
├── requirements.txt
└── requirements-dev.txt
```

## Run locally

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements-dev.txt
python -m pytest -v
python wsgi.py            # http://localhost:5000
```

Or with Docker:

```bash
docker build --target runtime -t flask-todo .
docker run -p 5000:5000 flask-todo
```

## Set up the pipeline on EC2

1. Launch an Ubuntu EC2 instance (t3.small recommended; t2.micro is tight for Jenkins).
2. Security group inbound rules: SSH (22) from your IP only, Jenkins (8080) from your IP only, HTTP (80) from anywhere.
3. Install Docker, Java 17 and Jenkins on the instance.
4. Add the Jenkins user to the Docker group and restart Jenkins:
   `sudo usermod -aG docker jenkins && sudo systemctl restart jenkins`
5. Open `http://<EC2-IP>:8080`, unlock Jenkins and install the suggested plugins.
6. Create a new **Pipeline** job. Choose "Pipeline script from SCM", select Git, enter your repo URL, and set the script path to `Jenkinsfile`.
7. In GitHub, go to Settings > Webhooks and add `http://<EC2-IP>:8080/github-webhook/` (content type `application/json`, push events).
8. In the Jenkins job, enable "GitHub hook trigger for GITScm polling".
9. Push a commit. The pipeline runs, and the app appears at `http://<EC2-IP>`.

## Demo the failure path

Break a test on purpose and push. The Test stage fails, the pipeline stops, and the
old version keeps running. Fix the test and push again to see it recover.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/todos` | List tasks |
| POST | `/api/todos` | Add a task (`{"title": "..."}`) |
| POST | `/api/todos/<id>/toggle` | Mark done or not done |
| DELETE | `/api/todos/<id>` | Delete a task |

## Possible improvements

- Push images to Docker Hub or AWS ECR and deploy from the registry
- Persist data with SQLite or PostgreSQL
- Add a linting stage (flake8) and Slack/email notifications on failure
- Provision the EC2 instance with Terraform
