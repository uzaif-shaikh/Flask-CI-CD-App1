# DeployFlow: CI/CD Pipeline for a Flask App with Jenkins, Docker and AWS EC2

DeployFlow is an automated CI/CD pipeline that takes a Flask to-do app from `git push` to a live, health-checked deployment on AWS EC2, with no manual steps. Every push to GitHub triggers Jenkins, which tests the code, builds a Docker image, deploys the container to EC2, and verifies the deployment is healthy.

The to-do app is intentionally small. The focus of this project is the pipeline around it.

## Pipeline Overview

```
GitHub push -> Webhook -> Jenkins
                            |-- 1. Checkout
                            |-- 2. Test         (pytest inside Docker build)
                            |-- 3. Build Image  (multi-stage, non-root, healthcheck)
                            |-- 4. Deploy       (docker run on EC2)
                            '-- 5. Smoke Test   (curl /health)
```

| Stage | What it does |
| ----- | ------------ |
| Checkout | Pulls the latest code from GitHub |
| Test | Runs the pytest suite inside the Docker build, so a failing test stops the pipeline |
| Build Image | Builds a multi-stage Docker image that runs as a non-root user and includes a healthcheck |
| Deploy | Replaces the running container on the EC2 instance with the new image |
| Smoke Test | Calls `/health` to confirm the new version is live |

If any stage fails, the pipeline stops and the previous version keeps running.

## Tech Stack

- **Language and framework:** Python 3.12, Flask, Gunicorn
- **Testing:** pytest
- **Containerization:** Docker (multi-stage build)
- **CI/CD:** Jenkins (declarative pipeline), GitHub webhooks
- **Cloud:** AWS EC2

## Project Structure

```
.
├── app/
│   ├── __init__.py          # Flask app factory and routes
│   └── templates/index.html
├── tests/test_app.py        # pytest tests
├── wsgi.py                  # Gunicorn entry point
├── Dockerfile               # test stage + runtime stage
├── Jenkinsfile              # pipeline definition
├── requirements.txt
└── requirements-dev.txt
```

## API Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/health` | Health check |
| GET | `/api/todos` | List tasks |
| POST | `/api/todos` | Add a task (`{"title": "..."}`) |
| POST | `/api/todos/<id>/toggle` | Mark a task done or not done |
| DELETE | `/api/todos/<id>` | Delete a task |

## Run Locally

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

## Set Up the Pipeline on EC2

1. Launch an Ubuntu EC2 instance (t3.small recommended; t2.micro is tight for Jenkins).
2. Set the security group inbound rules: SSH (22) from your IP only, Jenkins (8080) from your IP only, and HTTP (80) from anywhere.
3. Install Docker, Java 17 and Jenkins on the instance.
4. Add the Jenkins user to the Docker group and restart Jenkins:
   ```bash
   sudo usermod -aG docker jenkins && sudo systemctl restart jenkins
   ```
5. Open `http://<EC2-IP>:8080`, unlock Jenkins and install the suggested plugins.
6. Create a new **Pipeline** job. Choose "Pipeline script from SCM", select Git, enter your repo URL, and set the script path to `Jenkinsfile`.
7. In GitHub, go to Settings > Webhooks and add `http://<EC2-IP>:8080/github-webhook/` (content type `application/json`, push events).
8. In the Jenkins job, enable "GitHub hook trigger for GITScm polling".
9. Push a commit. The pipeline runs, and the app appears at `http://<EC2-IP>`.

## Demo: Failure Path

Break a test on purpose and push. The Test stage fails, the pipeline stops, and the old version keeps running. Fix the test and push again to watch the pipeline recover.

## Key Concepts Demonstrated

- Automated build, test and deploy on every commit
- Multi-stage Docker builds, where tests gate the final image
- Running containers as a non-root user, with a built-in healthcheck
- Webhook-triggered pipelines
- Post-deployment smoke testing

## Possible Improvements

- Push images to Docker Hub or AWS ECR and deploy from the registry
- Persist data with SQLite or PostgreSQL
- Add a linting stage (flake8) and Slack or email notifications on failure
- Provision the EC2 instance with Terraform

## Author

**Uzaif Shaikh**
GitHub: [@uzaif-shaikh](https://github.com/uzaif-shaikh)
