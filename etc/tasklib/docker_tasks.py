import os

from invoke import task

from .base import su_docker, runner

__all__ = [
    "docker_up",
    "docker_build",
    "docker_exec",
    "docker_attach",
    "docker_test",
    "docker_stop",
    "docker_rm",
    "docker_logs",
]


@task
def docker_up(ctx, dry_run=False):
    """
    Executes EJ on url http://localhost:8000
    """
    do = runner(ctx, dry_run, pty=True)
    file = "docker/docker-compose.yml"
    compose = f"docker-compose -f {file}"
    do(f"{compose} up  -d")


@task
def docker_build(ctx, dry_run=False, no_cache=False):
    """
    Build EJ web server image;
    """
    do = runner(ctx, dry_run, pty=True)
    file = "docker/docker-compose.yml"
    compose = f"docker-compose -f {file}"
    if no_cache:
        do(f"{compose} build  --no-cache")
    else:
        do(f"{compose} build")


@task
def docker_exec(ctx, command, dry_run=False, build=False):
    """
    Executes a command inside EJ web server container;
    """
    do = runner(ctx, dry_run, pty=True)
    do(f"docker exec --user=root -it  server /bin/bash -c 'source /root/.bashrc && {command}'")


@task
def docker_test(ctx, dry_run=False, build=False):
    """
    Runs EJ tests;
    """
    do = runner(ctx, dry_run, pty=True)
    do(f"docker exec --user=root -it  server /bin/bash -c 'source /root/.bashrc && inv test'")


@task
def docker_attach(ctx):
    """
    Connect to EJ web server container;
    """
    do = runner(ctx, dry_run=False, pty=True)
    do(f"docker exec -it server bash")


@task
def docker_stop(ctx):
    """
    Stop EJ containers;
    """
    do = runner(ctx, dry_run=False, pty=True)
    do(f"docker-compose -f docker/docker-compose.yml stop")


@task
def docker_rm(ctx):
    """
    Remove EJ containers;
    """
    do = runner(ctx, dry_run=False, pty=True)
    do(f"docker-compose -f docker/docker-compose.yml rm")


@task
def docker_logs(ctx):
    """
    Follows EJ web server log;
    """
    do = runner(ctx, dry_run=False, pty=True)
    do(f"docker logs -f server")
