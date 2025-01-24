from typing import Annotated
from fastapi import APIRouter, Depends
import docker
import uuid
import os
from app.schemas import SubmissionCreate
from app.users import current_active_user
from app.db import User

IMAGE = "python:3.9-slim"
RESOURCE_LIMITS = {"memory": "256m", "cpus": "0.5"}

docker_client = docker.from_env()

def get_submissions_router() -> APIRouter:
    router = APIRouter()

    @router.get("/")
    async def root():
        return {"message": "server running"}

    @router.post("/run")
    async def run(submission: SubmissionCreate, user: User = Depends(current_active_user)):
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

    return router
