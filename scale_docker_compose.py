import os
import argparse

parser = argparse.ArgumentParser(description="Скрипт для формирования oocker-compose.yml")
parser.add_argument("num", type=int, help="Кол-во стендов")
args = parser.parse_args()
BASE_PORT = 3000


def new_instance_exam(num: int):
    global BASE_PORT
    template_intance = f"""
    vpwa_main_{BASE_PORT}:
        build:
            context: .
            dockerfile: DockerfileVPWA
        ports:
            - '{BASE_PORT}:6177'
        stdin_open: true
        tty: true
        pids_limit: 100
        mem_limit: 512M
        cpus: 0.25
    bot_xss_{BASE_PORT + 1000}:
        build:
            context: .
            dockerfile: DockerfileBot
        environment:
            name_service: 'vpwa_main_{BASE_PORT}'
        ports:
            - '{BASE_PORT + 1000}:6177'
        stdin_open: true
        tty: true
        pids_limit: 100
        mem_limit: 128M
        cpus: 0.25
"""
    BASE_PORT += 1
    return template_intance


template_yml = 'services:\n'
for i in range(args.num):
    template_yml += new_instance_exam(i)

with open("docker-compose.yml", "w", encoding="utf-8") as file:
    file.write(template_yml)
