import json
import docker
import requests

client = docker.from_env()

# malicious_cmd = "\"; sleep 10; echo \"evil"
# malicious_cmd = """
# import os
# print(1234)
# while True:
#     pid = os.fork()
#     print(f'pid: {pid}')
# """
malicious_cmd = "print(12)"

nproc_limit = docker.types.Ulimit(name="nproc", hard=3)
# stack_size_limit = docker.types.Ulimit(name="stack", hard=1000)

class DockerTaskException(Exception):
    pass

try:
    container = client.containers.run(
        "python:3.8-alpine",
        ["sh", "-c", f"echo test | python -c \"{malicious_cmd}\""],
        # ["sh", "-c", ":(){ :|:& };:"],
        detach=True,
        mem_limit="4m",
        memswap_limit="4m",
        # auto_remove=True,
        # remove=True,
        network_disabled=True,
        network_mode="none",
        pids_limit=3,
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
