# Functions

## Receive files via

- File Transport Automation Client
- API (REST, python)

## Download files from

- FTP/FTPS
- SFTP
- Local directory
- CIFS/SMD share

## Process files

- Rename
- Run script: python, bash...
- Unprocess/Compress files

## Upload files to

- FTP/FTPS
- SFTP
- Local directory
- CIFS/SMD share

# Start File Transport Automation

## Docker

```bash
docker run --name some-file-transfer-automation \
-v $PWD/work:/app/work \
-e MYSQL_HOST=localhost \
-e MYSQL_USER=username \
-e MYSQL_PASS=password \
-e MYSQL_DB=file_transfer_automation \
-d -p 8080:8080 ghcr.io/fr3h4g/file-transfer-automation:latest
```

## Environment Variables

### MYSQL_HOST

### MYSQL_USER

### MYSQL_PASS

### MYSQL_DB

# Development

```cmd
docker-compose up --build
```
