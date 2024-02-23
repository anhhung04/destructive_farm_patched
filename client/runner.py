import re
import os
import sys
import time
import shlex
import argparse
import threading
import subprocess
import requests
from importlib import import_module
from core import truncate, logger
from core.handler import SubmitClient

exploit_name = ''
handler: SubmitClient = None
game_config = {}


def main(args):
    global exploit_name, handler, game_config
    
    game_config = load_game_config(args.server_url)
    exploit_name = args.name
    handler = SubmitClient(args.server_url, args.auth)

    if args.run:
        exploit_func = exploit_func_from_shell(args.run)
        prepare_func = None
        cleanup_func = None
    else:
        sys.path.append(os.getcwd())
        module = import_module(f'{args.module}')
        exploit_func = getattr(module, 'exploit')
        prepare_func = getattr(module, 'prepare', None)
        cleanup_func = getattr(module, 'cleanup', None)

    threads = [
        threading.Thread(
            target=exploit_wrapper,
            name=target,
            args=(exploit_func, target, game_config['TEAMS'][target],))
        for target in game_config['TEAMS']
    ]

    if prepare_func:
        prepare_func()


    for t in threads:
        t.start()

    for t in join_threads(threads, args.timeout):
        logger.error(f"{(exploit_name)} took longer than {(str(args.timeout))} seconds for {(t.name)}. ⌛")    

    if cleanup_func:
        cleanup_func()


def load_game_config(server_url):
    cfg = requests.get(server_url + '/api/get_config').json()
    return cfg

def exploit_wrapper(exploit_func, target, target_ip):
    try:
        response_text = exploit_func(target_ip)
        found_flags = match_flags(response_text)
        

        if found_flags:
            response = handler.enqueue(found_flags, exploit_name, target)
            if 'own' in response:
                logger.warning(f"{(exploit_name)} retrieved own flag! Patch the service ASAP.")
                return
            elif 'pending' in response:
                logger.warning(f"{(exploit_name)} retrieved {response['pending']} flag{'s' if response['pending'] > 1 else ''}, but there is no connection to the server.")
                return
            if response['status'] == 'ok':
                logger.success(
                    f"{(exploit_name)} retrieved {len(found_flags)} flag{'s' if len(found_flags) > 1 else ''} from {(target)}.")
        else:
            logger.warning(
                f"{(exploit_name)} retrieved no flags from {(target)}. — {repr(truncate(response_text, 50))}")
    except Exception as e:
        logger.error(
            f"{(exploit_name)} failed with an error for {(target)}:\n-------\n {(e)} \n-------\n")

def exploit_func_from_shell(command):
    def exploit_func(target):
        rendered_command = shlex.join([target if value ==
                                       '[ip]' else value for value in shlex.split(command)])
        return run_shell_command(rendered_command)

    return exploit_func


def run_shell_command(command):
    return subprocess.run(
        command,
        capture_output=True,
        shell=True,
        text=True
    ).stdout.strip()


def match_flags(text):
    matches = re.findall(game_config["FLAG_FORMAT"], text)
    return matches if matches else None


def join_threads(threads, timeout):
    start = now = time.time()
    while now <= (start + timeout):
        for thread in threads:
            if thread.is_alive():
                thread.join(timeout=0)
        if all(not t.is_alive() for t in threads):
            return []
        time.sleep(0.1)
        now = time.time()
    else:
        return [t for t in threads if t.is_alive()]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run exploits in parallel for given IP addresses.")
    parser.add_argument("--name", metavar="Name", type=str,
                        required=True, help="Name of the exploit for its identification")
    parser.add_argument("--module", metavar="Exploit", type=str,
                        help="Name of the module containing the 'exploit' function")
    parser.add_argument("--run", metavar="Command", type=str,
                        help="Optional shell command for running the exploit if it is not a Python script")
    parser.add_argument("--timeout", type=int, default=30,
                        help="Optional timeout for exploit in seconds")
    parser.add_argument("--server-url", type=str, default="http://localhost:5000")

    parser.add_argument("--auth", type=str, default=None)
    
    args = parser.parse_args()
    main(args)
