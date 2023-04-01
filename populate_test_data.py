"""Populate test data for dev."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from filetransferautomation import models

SQLALCHEMY_DATABASE_URL = "sqlite:///test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    # echo=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

db = SessionLocal()

sql = []
sql.append(
    models.Host(
        host_id=1,
        name="test local input",
        type="local_directory",
        directory="./test-input",
    )
)
sql.append(
    models.Host(
        host_id=2,
        name="test local output",
        type="local_directory",
        directory="./test-output",
    )
)
sql.append(
    models.Schedule(
        schedule_id=1,
        task_id=1,
        cron="*/1 * * * *",
    )
)
sql.append(
    models.Step(step_id=1, task_id=1, host_id=1, file_mask="*.txt", step_type="source")
)
sql.append(
    models.Step(
        step_id=2, task_id=1, host_id=2, file_mask="*.txt", step_type="destination"
    )
)
sql.append(models.Process(process_id=1, name="test", script_file="test.py"))
sql.append(
    models.Step(step_id=3, task_id=1, host_id=2, step_type="process", process_id=1)
)
sql.append(models.Task(task_id=1, name="test", description="", active=1))
db.add_all(sql)
db.commit()
