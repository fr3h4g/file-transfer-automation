"""FTP client."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import SupportsRead

import ftplib
from ftplib import FTP


class FTPClient:
    """FTP client."""

    _connection = None
    _file_data = b""

    def __init__(self, hostname: str, username: str, password: str):
        """Connect to FTP."""
        self._connection = FTP(
            host=hostname, user=username, passwd=password, timeout=10
        )

    def _check_if_dir(self, item_name: str) -> bool:
        """Check if it's a directory."""
        if self._connection:
            try:
                self._connection.cwd(item_name)
                self._connection.cwd("..")
                return True
            except ftplib.error_perm:
                return False
        return False

    def list_dir(self) -> list:
        """List files."""
        file_list = []
        if self._connection:
            for filename in self._connection.nlst():
                if not self._check_if_dir(filename):
                    file_list.append(filename)
        return file_list

    def chdir(self, path: str):
        """Change directory."""
        if self._connection:
            self._connection.cwd(path)

    def get_file(self, filename: str):
        """Download remote file."""
        self._file_data = b""
        if self._connection:
            self._connection.retrbinary(
                f"RETR {filename}", callback=self.receive_file_object_cb
            )
        return self._file_data

    def send_file(self, filename: str, file_data: SupportsRead[bytes]) -> bool:
        """Upload file to remote."""
        if self._connection:
            try:
                self._connection.storbinary(f"STOR {filename}", file_data)
            except ftplib.all_errors:
                return False
            else:
                return True
        return False

    def receive_file_object_cb(self, data: bytes):
        """Receive file data."""
        self._file_data += data

    def remove(self, filename: str):
        """Delete remote file."""
        if self._connection:
            self._connection.delete(filename)

    def rename(self, filename_from: str, filename_to: str):
        """Rename remote file."""
        if self._connection:
            self._connection.rename(filename_from, filename_to)

    def close(self):
        """Close connection."""
        if self._connection:
            self._connection.close()
