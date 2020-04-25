import json
import docker
import requests
import os
import pathlib

from dotenv import load_dotenv
load_dotenv()

client = docker.from_env()
TMP_DIR = os.path.abspath("tmp")

def execute_code(input_filename, code_filename):

    tmp_mount = docker.types.Mount("/home/agent/mnt", TMP_DIR, type="bind")

    args = [
        "--file", os.path.join("mnt", code_filename),
        "--input", input_filename,
        "--timeout", "2.0",
        "--result", "mnt/results.json",
        "--error", "mnt/err.log"
    ]

    command = [
        "python",
        "agent.py"
    ] + args

    print(command)

    logs = client.containers.run(
        os.getenv("IMAGE"),
        command,
        mounts=[tmp_mount],
        network_disabled=True,
        network_mode="none"
    )

    print(logs)

    resfile = os.path.join(TMP_DIR, 'results.json')
    with open(resfile, 'r') as f:
        results = json.load(f)
        print(results)

execute_code("add_two", "submission.py")