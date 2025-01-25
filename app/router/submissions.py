from typing import Annotated
from fastapi import APIRouter, Depends
import docker
import uuid
import os
from app.schemas import SubmissionCreate
from app.users import current_active_user
from app.db import User
import time

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
            input_data = submission.input_data
            if input_data is None: input_data = ""
            if language=="python":
                IMAGE = "python:3.9-slim"
                code_file = f"/tmp/{uuid.uuid4()}.py"
                with open(code_file, "w") as f:
                    f.write(code)
                with open(code_file+"input", "w") as f:
                    f.write(input_data + "\r\n")
                container = docker_client.containers.create(
                    image=IMAGE,
                    command="bash",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    tty=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
                container.start()
                execution_result = container.exec_run(["sh", "-c", f"cat {os.path.basename(code_file)+'input'} | python {os.path.basename(code_file)}"])
                output = execution_result.output.decode("utf-8")
                container.stop()
            elif language=="c":
                IMAGE = "gcc:latest"
                code_file = f"/tmp/{uuid.uuid4()}.c"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.create(
                    image=IMAGE,
                    command="bash",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    tty=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
                container.start()
                compile_command = f"g++ {os.path.basename(code_file)} -o {os.path.basename(code_file)}.out"
                compile_result = container.exec_run(compile_command)
                if compile_result.exit_code != 0:
                    raise RuntimeError(f"Compilation failed: {compile_result.output.decode('utf-8')}")
                execute_command = ["sh", "-c", f"cat {os.path.basename(code_file)+'input'} | ./{os.path.basename(code_file)}.out"]
                execution_result = container.exec_run(execute_command)
                output = execution_result.output.decode('utf-8')
                container.stop()
                container.remove()
            elif language == "cpp":
                IMAGE = "gcc:latest"
                code_file = f"/tmp/{uuid.uuid4()}.cpp"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.create(
                    image=IMAGE,
                    command="bash",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    tty=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
                container.start()
                compile_command = f"g++ {os.path.basename(code_file)} -o {os.path.basename(code_file)}.out"
                compile_result = container.exec_run(compile_command)
                if compile_result.exit_code != 0:
                    raise RuntimeError(f"Compilation failed: {compile_result.output.decode('utf-8')}")
                execute_command = ["sh", "-c", f"cat {os.path.basename(code_file)+'input'} | ./{os.path.basename(code_file)}.out"]
                execution_result = container.exec_run(execute_command)
                output = execution_result.output.decode("utf-8")
                container.stop()
                container.remove()
            elif language == "java":
                IMAGE = "eclipse-temurin:21"
                code_file = f"/tmp/{uuid.uuid4()}.java"
                with open(code_file, "w") as f:
                    f.write(code)
                class_name = os.path.basename(code_file).replace(".java", "")
                container = docker_client.containers.create(
                    image=IMAGE,
                    command="bash",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    tty=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
                container.start()
                compile_command = f"javac {os.path.basename(code_file)}"
                compile_result = container.exec_run(compile_command)
                if compile_result.exit_code != 0:
                    raise RuntimeError(f"Compilation failed: {compile_result.output.decode('utf-8')}")
                execute_command = ["sh", "-c", f"cat {os.path.basename(code_file)+'input'} | java -cp . $(ls *.class | sed 's/.class$//')"]
                execution_result = container.exec_run(execute_command)
                output = execution_result.output.decode("utf-8")
                container.stop()
                container.remove()
            elif language == "javascript":
                IMAGE = "node:18"
                code_file = f"/tmp/{uuid.uuid4()}.js"
                with open(code_file, "w") as f:
                    f.write(code)
                container = docker_client.containers.create(
                    image=IMAGE,
                    command="bash",
                    volumes={os.path.dirname(code_file): {"bind": "/code", "mode": "rw"}},
                    working_dir="/code",
                    tty=True,
                    mem_limit=RESOURCE_LIMITS["memory"],
                    nano_cpus=int(float(RESOURCE_LIMITS["cpus"]) * 1e9)
                )
                container.start()
                execution_command=["sh", "-c", f"cat {os.path.basename(code_file)+'input'} | node {os.path.basename(code_file)}"]
                execution_result = container.exec_run(execute_command)
                output = execution_result.output.decode("utf-8")
                container.stop()
                container.remove()
            else:
                return "Error: Language not supported"
            return output

        except docker.errors.ContainerError as e:
            return {"error:",str(e)}

    return router
