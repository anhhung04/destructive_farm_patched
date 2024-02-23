#! /usr/bin/env python3
from core import *
import argparse
import os
import threading
import subprocess
from apscheduler.schedulers.blocking import BlockingScheduler

DIR_PATH = os.path.dirname(os.path.realpath(__file__))
RUNNER_PATH = os.path.join(DIR_PATH, 'runner.py')

def main(args):
    global server_url, exploit_name, timeout, handler
    server_url = args.server_url
    exploit_name = args.name or 'sploit_client'
    timeout = args.time_out
    handler = create_handler(args.server_url, args.auth)
    cfg = load_config(server_url)

    scheduler = BlockingScheduler()
    scheduler.add_job(
        func=run_exploits,
        trigger='interval',
        seconds=cfg["TICK_PERIOD"],
        id='exploits',
        next_run_time=seconds_from_now(0)
    )

    scheduler.add_job(
        func=enqueue_from_fallback,
        trigger='interval',
        seconds=cfg["TICK_PERIOD"]/2,
        id='fallback_flagstore',
        next_run_time=seconds_from_now(0)
    )

    scheduler.start()


def enqueue_from_fallback():
    flags = [flag for flag in FallbackFlag.select().where(FallbackFlag.status == 'pending')]
    if flags:
        logger.info(f'Forwarding {len(flags)} flags from the fallback flagstore...')
        handler.enqueue_from_fallback(flags)

def load_exploits():
    exploit_scripts = []
    for script in os.listdir('./exploits'):
        if script.endswith('.py'):
            exploit_scripts.append('exploits.' + script[0:-3])
    return exploit_scripts


def run_exploits():
    exploits = load_exploits()
    if not exploits:
        logger.info(f'No exploits cannot be found.')
        return

    for exploit in exploits:
        threading.Thread(target=run_exploit, args=(exploit,)).start()


def run_exploit(exploit):
    runner_command = ['python', RUNNER_PATH] + ['--name',exploit_name]
    runner_command.extend(['--module', exploit])
    runner_command.extend(['--timeout', str(timeout)])

    logger.info(
        f'Running {exploit} ...')
    subprocess.run(runner_command, text=True, env={**os.environ})
    logger.info(f'{exploit} finished.')


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-url", type=str,
                        default="http://localhost:5000")
    parser.add_argument("--auth", type=str, default=None)
    parser.add_argument("--time-out", type=int, default=30)
    parser.add_argument("--name", type=str, default=None)
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())
