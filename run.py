import json
import docker
import requests
import os
import pathlib

from dotenv import load_dotenv
load_dotenv()

client = docker.from_env()

# malicious_cmd = "\"; sleep 10; echo \"evil"
malicious_cmd = """print(input())"""
malicious_cmd = "print(12)"

nproc_limit = docker.types.Ulimit(name="nproc", hard=3)

input_path = os.path.abspath("inputs")
programs_path = os.path.abspath("tmp")

input_mount = docker.types.Mount("/inputs/", input_path, read_only=True, type="bind")
tmp_mount   = docker.types.Mount("/tmp/", programs_path, type="bind")

class DockerTaskException(Exception):
    pass

def execute_code(input_filename, code_filename):
    try:
        command = ["sh", "-c", f"python {code_filename} < {input_filename}"]
        print(command)
        container = client.containers.run(
            os.getenv("IMAGE"),
            command,
            # ["sh", "-c", ":(){ :|:& };:"],
            detach=True,
            mem_limit=os.getenv("MEM_LIMIT"),
            memswap_limit=os.getenv("MEM_LIMIT"),
            # auto_remove=True,
            # remove=True,
            mounts=[
                input_mount,
                tmp_mount
            ],
            network_disabled=True,
            network_mode="none",
            pids_limit=int(os.getenv("PID_LIMIT")),
            read_only=True,
            ulimits=[
                nproc_limit,
            ]
        )

        exit_code = container.wait(timeout=5)
        logs = container.logs()
        
        if (exit_code['StatusCode'] != 0):
            raise DockerTaskException((exit_code, logs))

        print(logs)

    except requests.exceptions.ConnectionError as err:
        print(f"timeout err: the container was executing for too long")

    except docker.errors.ContainerError as err:
        print(f"some container error: {err}")

    except DockerTaskException as err:
        print(err)

    finally:
        container.stop(timeout=0)
        container.remove()

execute_code("/inputs/input.txt", "/tmp/test.py")