"""Hosts data."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class Host:
    """Host dataclass."""

    type: Literal["local_directory"] | Literal["unc_share"]
    host_id: int | None = None
    directory: str | None = None
    share: str | None = None
    username: str | None = None
    password: str | None = None


HOSTS: list[Host] = []


def load_hosts():
    """Load hosts from database."""
    global HOSTS
    HOSTS.append(Host(host_id=1, type="local_directory", directory="./test-input"))
    HOSTS.append(Host(host_id=2, type="local_directory", directory="./test-output"))
    HOSTS.append(
        Host(
            host_id=3,
            type="unc_share",
            share="\\\\testserver\\test_share",
            username="username",
            password="password",
        )
    )
    return HOSTS


def get_host(host_id: int) -> Host | None:
    """Get a host."""
    for host in HOSTS:
        if host and host.host_id == host_id:
            return host
    return None
