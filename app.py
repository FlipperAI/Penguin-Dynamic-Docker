from typing import Annotated
from fastapi import FastAPI, Form
import docker
import uuid
import os

from pydantic import BaseModel

class Submission(BaseModel):
    code: str
    language: str

IMAGE = "python:3.9-slim"
RESOURCE_LIMITS = {"memory": "256m", "cpus": "0.5"}

app = FastAPI()
docker_client = docker.from_env()

@app.get("/")
async def root():
    return {"message": "server running"}

@app.post("/run")
async def run(submission: Submission):
    try:
        code = submission.code
        language = submission.language
        code_file = f"/tmp/{uuid.uuid4()}.py"
        with open(code_file, "w") as f:
            f.write(code)
        container = docker_client.containers.run(
            image=IMAGE,
            command=f"python {os.path.basename(code_file)}",
            volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
            working_dir="/code",
            remove=True,
            detach=True,
            mem_limit=RESOURCE_LIMITS["memory"],
            nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
        )

        output = container.logs().decode("utf-8")
        return output
    except docker.errors.ContainerError as e:
        return {"error": str(e)}
