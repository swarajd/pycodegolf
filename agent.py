import os
import json
import argparse
import time
import resource
import threading
import subprocess

from collections import namedtuple

description = "Agent that runs submission"

MAX_SYSTEM_RUNTIME = 60 * 5
MAX_OUTPUT_SIZE = 1024 * 1024 * 124
MAX_FD = 10

# TODO: alter for code golf stats
submission_result = namedtuple('submission_result', ['status', 'size'])

# TODO: alter for golf stats
def log_results(resultfile, results):
    obj = {
        'status': results.status,
        'size': results.size,
    }
    with open(resultfile, 'w') as output:
        json.dump(obj, output)

def process_setup():
    resource.setrlimit(resource.RLIMIT_CPU, (MAX_SYSTEM_RUNTIME, MAX_SYSTEM_RUNTIME))
    resource.setrlimit(resource.RLIMIT_NOFILE, (MAX_FD, MAX_FD))
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT_SIZE, MAX_OUTPUT_SIZE))

def wait_for_process(proc):
    return proc.wait()

def run_submission(filename, infile, timeout, errfile):
    command = ["python3", filename]
    status = 'OK'
    outfile = infile + '.out'
    fds = (infile, outfile, errfile)

    print(os.getcwd())
    print(os.listdir())
    # return submission_result(status, 5)

    program_size = os.path.getsize(filename)

    infile, outfile, errfile = fds

    with open(infile, 'r') as infd:
        with open(outfile, 'w') as outfd:
            with open(errfile, 'a') as errfd:
                proc = subprocess.Popen(
                    command,
                    stdin=infd,
                    stdout=outfd,
                    stderr=errfd,
                    preexec_fn=process_setup
                )

    start = time.time()

    thread = threading.Thread(target=wait_for_process, args=(proc,))
    thread.start()
    thread.join(timeout=timeout)

    runtime = time.time() - start
    status = 'OK'
    if thread.is_alive():
        status = 'TO'

        proc.kill()
        thread.join()
    elif proc.returncode != 0:
        status = 'RE'

    return submission_result(status, program_size)

def create_file(filename):
    """Creates or truncates a file
    :param filename: filename to create
    """
    fd = open(filename, 'w')
    fd.close()

def main():
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        "--file", 
        required=True, 
        help="filename of submission"
    )
    parser.add_argument(
        "--timeout",
        required=True,
        help="timeout of code in seconds",
        type=float
    )

    parser.add_argument(
        "--result",
        required=True,
        help="result file"
    )

    parser.add_argument(
        "--error",
        required=True,
        help="stderr log file"
    )

    parser.add_argument(
        "--input",
        required=True,
        help="input file to run"
    )

    args = parser.parse_args()

    input_file = args.input
    workdir, submission_file = os.path.split(args.file)
    result_file = os.path.realpath(args.result)
    error_file = os.path.realpath(args.error)

    create_file(error_file)
    os.chdir(workdir)

    print(workdir, submission_file, args.file)

    # TODO: alter for golf stats
    result = run_submission(submission_file, input_file, args.timeout, error_file)
    log_results(result_file, result)

if __name__ == "__main__":
    main()