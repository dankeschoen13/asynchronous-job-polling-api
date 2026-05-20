from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import Job
import logging

logger = logging.getLogger(__name__)

class JobSvc:

    @classmethod
    def _active_jobs_query(cls):

        return db.select(Job)

    @classmethod
    def fetch_by_id(cls, job_id: int) -> Job | None:

        stmt = cls._active_jobs_query().where(Job.id == job_id)

        return db.session.execute(stmt).scalar_one_or_none()

    @classmethod
    def create_job(cls, report_type: str):

        new_job = Job(report_type=report_type)

        try:
            db.session.add(new_job)
            db.session.commit()

        except IntegrityError as e:

            logger.error(f"Unable to save report: {e}")

            db.session.rollback()
            raise ValueError("Unable to save report.")

        return new_job