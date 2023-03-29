"""Hosts data."""
from __future__ import annotations

from filetransferautomation.models import Host

HOSTS: list[Host] = []


def load_hosts():
    """Load hosts from database."""
    global HOSTS
    HOSTS.append(
        Host(
            host_id=1,
            type="local_directory",
            directory="./test-input",
            name="test input dir on local host",
        )
    )
    HOSTS.append(
        Host(
            host_id=2,
            type="local_directory",
            directory="./test-output",
            name="test output dir on local host",
        )
    )
    HOSTS.append(
        Host(
            host_id=3,
            type="unc_share",
            share="\\\\testserver\\test_share",
            username="username",
            password="password",
            name="test share on testserver",
        )
    )
    return HOSTS


def get_host(host_id: int) -> Host | None:
    """Get a host."""
    for host in HOSTS:
        if host and host.host_id == host_id:
            return host
    return None
