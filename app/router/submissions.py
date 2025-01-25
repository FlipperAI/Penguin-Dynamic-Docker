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
            if language=="python":
                IMAGE = "python:3.9-slim"
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
            elif language=="java":
                IMAGE = "openjdk:11"
                code_file = f"/tmp/{uuid.uuid4()}.java"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"javac {os.path.basename(code_file)} && java {os.path.basename(code_file).replace('.java', '')}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="c":
                IMAGE = "gcc:latest"
                code_file = f"/tmp/{uuid.uuid4()}.c"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"gcc {os.path.basename(code_file)} -o {os.path.basename(code_file).replace('.c', '')} && ./{os.path.basename(code_file).replace('.c', '')}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="cpp":
                IMAGE = "gcc:latest"
                code_file = f"/tmp/{uuid.uuid4()}.cpp"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"g++ {os.path.basename(code_file)} -o {os.path.basename(code_file).replace('.cpp', '')} && ./{os.path.basename(code_file).replace('.cpp', '')}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="javascript":
                IMAGE = "node:14"
                code_file = f"/tmp/{uuid.uuid4()}.js"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"node {os.path.basename(code_file)}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="ruby":
                IMAGE = "ruby:2.7"
                code_file = f"/tmp/{uuid.uuid4()}.rb"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"ruby {os.path.basename(code_file)}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="php":
                IMAGE = "php:7.4"
                code_file = f"/tmp/{uuid.uuid4()}.php"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"php {os.path.basename(code_file)}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="go":
                IMAGE = "golang:1.16"
                code_file = f"/tmp/{uuid.uuid4()}.go"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"go run {os.path.basename(code_file)}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="rust":
                IMAGE = "rust:1.53"
                code_file = f"/tmp/{uuid.uuid4()}.rs"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"rustc {os.path.basename(code_file)} && ./{os.path.basename(code_file).replace('.rs', '')}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="swift":
                IMAGE = "swift:5.4"
                code_file = f"/tmp/{uuid.uuid4()}.swift"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"swift {os.path.basename(code_file)}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="kotlin":
                IMAGE = "kotlin:1.5"
                code_file = f"/tmp/{uuid.uuid4()}.kt"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"kotlinc {os.path.basename(code_file)} -include-runtime -d {os.path.basename(code_file).replace('.kt', '.jar')} && java -jar {os.path.basename(code_file).replace('.kt', '.jar')}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="scala":
                IMAGE = "scala:2.13"
                code_file = f"/tmp/{uuid.uuid4()}.scala"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"scalac {os.path.basename(code_file)} && scala {os.path.basename(code_file).replace('.scala', '')}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="r":
                IMAGE = "r-base:latest"
                code_file = f"/tmp/{uuid.uuid4()}.r"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"Rscript {os.path.basename(code_file)}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="perl":
                IMAGE = "perl:latest"
                code_file = f"/tmp/{uuid.uuid4()}.pl"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"perl {os.path.basename(code_file)}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="bash":
                IMAGE = "alpine:latest"
                code_file = f"/tmp/{uuid.uuid4()}.sh"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"apk add bash && bash {os.path.basename(code_file)}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="powershell":
                IMAGE = "mcr.microsoft.com/powershell:latest"
                code_file = f"/tmp/{uuid.uuid4()}.ps1"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"pwsh {os.path.basename(code_file)}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="typescript":
                IMAGE = "node:14"
                code_file = f"/tmp/{uuid.uuid4()}.ts"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"tsc {os.path.basename(code_file)} && node {os.path.basename(code_file).replace('.ts', '.js')}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            elif language=="lua":
                IMAGE = "lua:latest"
                code_file = f"/tmp/{uuid.uuid4()}.lua"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.run(
                    image=IMAGE,
                    command=f"lua {os.path.basename(code_file)}",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    remove=True,
                    detach=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
            else:
                return {"error": "language not supported"}
            container.wait()
            output = container.logs().decode("utf-8")
            return output
        except docker.errors.ContainerError as e:
            return {"error": str(e)}

    return router
