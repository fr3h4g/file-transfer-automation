"""Populate test data for dev."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from filetransferautomation import models, settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    # connect_args={"check_same_thread": False},
    # echo=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

models.Base.metadata.create_all(bind=engine)

with SessionLocal() as db:
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
        models.Step(
            sort_order=20,
            step_id=2,
            task_id=1,
            host_id=1,
            script="local_directory_download_files",
            arguments='{"file_filter":"*.txt"}',
        )
    )
    sql.append(
        models.Step(
            sort_order=30,
            step_id=3,
            task_id=1,
            host_id=2,
            script="local_directory_upload_files",
            arguments='{"file_filter":"*.txt"}',
        )
    )
    sql.append(models.Task(task_id=1, name="test", description="", active=1))
    db.add_all(sql)
    db.commit()
