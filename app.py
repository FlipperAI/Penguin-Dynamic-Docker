
from flask import Flask, request, jsonify
import docker
import uuid
import os

app = Flask(__name__)
docker_client = docker.from_env()

# Constants for container configuration
IMAGE = "python:3.9-slim"
RESOURCE_LIMITS = {"memory": "256m", "cpus": "0.5"}

@app.route('/run', methods=['POST'])
def run_code():
    try:
        # Parse code submission
        data = request.json
        code = data.get("code")
        language = data.get("language", "python")
        
        if not code:
            return jsonify({"error": "Code is required"}), 400
        
        # Create a temporary file with the submitted code
        code_file = f"/tmp/{uuid.uuid4()}.py"
        with open(code_file, "w") as f:
            f.write(code)
        
        # Create and run the container
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
        
        # Capture container output
        output = container.logs().decode("utf-8")
        return jsonify({"output": output}), 200
    except docker.errors.ContainerError as e:
        return jsonify({"error": "Execution failed", "details": str(e)}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
