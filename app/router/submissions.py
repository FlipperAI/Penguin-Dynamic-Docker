from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response
import docker
import uuid
import os
from app.schemas import SubmissionCreate
from app.users import current_active_user
from app.db import User
import asyncio
import time
import signal

RESOURCE_LIMITS = {"memory": "256m", "cpus": "0.5"}

docker_client = docker.from_env()

async def stop_and_remove_container(container):
    await asyncio.to_thread(container.stop)  # Offload blocking call to a thread
    await asyncio.to_thread(container.remove)  # Offl

def handler(signum, frame):
    raise Exception("time's up")

def get_submissions_router() -> APIRouter:
    router = APIRouter()

    @router.post("/run")
    async def run(submission: SubmissionCreate, response: Response, user: User = Depends(current_active_user)):
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


                execute_command = ["sh", "-c", f"cat {os.path.basename(code_file)+'input'} | python {os.path.basename(code_file)}"]
            elif language=="c":
                IMAGE = "gcc:latest"
                code_file = f"/tmp/{uuid.uuid4()}.c"
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
                compile_command = f"g++ {os.path.basename(code_file)} -o {os.path.basename(code_file)}.out"
                compile_result = container.exec_run(compile_command)
                if compile_result.exit_code != 0:
                    raise RuntimeError(f"Compilation failed: {compile_result.output.decode('utf-8')}")
                execute_command = ["sh", "-c", f"cat {os.path.basename(code_file)+'input'} | ./{os.path.basename(code_file)}.out"]
            elif language == "cpp":
                IMAGE = "gcc:latest"
                code_file = f"/tmp/{uuid.uuid4()}.cpp"
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
                compile_command = f"g++ {os.path.basename(code_file)} -o {os.path.basename(code_file)}.out"
                compile_result = container.exec_run(compile_command)
                if compile_result.exit_code != 0:
                    raise RuntimeError(f"Compilation failed: {compile_result.output.decode('utf-8')}")
                execute_command = ["sh", "-c", f"cat {os.path.basename(code_file)+'input'} | ./{os.path.basename(code_file)}.out"]
            elif language == "java":
                IMAGE = "eclipse-temurin:21"
                code_file = f"/tmp/{uuid.uuid4()}.java"
                with open(code_file, "w") as f:
                    f.write(code)
                with open(code_file+"input", "w") as f:
                    f.write(input_data + "\r\n")
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
            elif language == "javascript":
                IMAGE = "node:18"
                code_file = f"/tmp/{uuid.uuid4()}.js"
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
                execution_command=["sh", "-c", f"cat {os.path.basename(code_file)+'input'} | node {os.path.basename(code_file)}"]
            else:
                return "Error: Language not supported"
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(30)
            try:
                start_time = time.perf_counter()  # Start timing
                execution_result = container.exec_run(execute_command, demux=True)
                end_time = time.perf_counter()  # End timing
                stdout = execution_result.output[0]
                if stdout is None: stdout = bytes()
                stderr = execution_result.output[1]
                if stderr is None: stderr = bytes()
                output = {"exit_code": execution_result.exit_code, "stdout": stdout.decode('utf-8'), "stderr":stderr.decode('utf-8'), "exec_time": end_time- start_time}
                if execution_result.exit_code != 0:
                    output = {"exit_code": execution_result.exit_code, "stdout": stdout.decode('utf-8'), "stderr":stderr.decode('utf-8'), "exec_time": end_time- start_time}
                    response.status_code=status.HTTP_401_BAD_REQUEST
            except Exception as e:
                output = {"exit_code": -1, "stdout":"", "stderr": "timed out waiting for code to run"}
                response.status_code=status.HTTP_400_BAD_REQUEST
            asyncio.create_task(stop_and_remove_container(container))

        except Exception as e:
            output = {"exit_code": -1, "stdout":"", "stderr": str(e)}
            response.status_code=status.HTTP_500_INTERNAL_SERVER_ERROR

        return output

    return router
