from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models import Job, TicketStatus
import logging

logger = logging.getLogger(__name__)

class JobSvc:

    @classmethod
    def _active_jobs_query(cls):
        """
        Helper method to select Job instance ordered by date_submitted
        """
        return db.select(Job).order_by(Job.date_submitted)

    @classmethod
    def fetch_by_id(cls, job_id: int) -> Job | None:
        """
        Fetches the Job object that matches the id

        Returns:
            Job | None: The matching Job object or none
        """
        stmt = cls._active_jobs_query().where(Job.id == job_id)

        return db.session.execute(stmt).scalar_one_or_none()

    @classmethod
    def fetch_pending(cls, limit: int = 10) -> list[Job]:
        """
        Fetches a list of all pending job orders from the
        database

        Args:
            limit: requested limit of pending job orders to be fetched.
            Defaults to 10

        Returns:
            list[Job]: A list of matching Job objects
        """
        stmt = cls._active_jobs_query().where(
            Job.status == TicketStatus.PENDING
        ).limit(limit)

        return db.session.scalars(stmt).all()

    @classmethod
    def save_changes(cls, job_obj: Job) -> tuple[bool, str | None]:
        """
        Commits any pending session changes to the database safely.

        Returns:
            tuple[bool, str | None]: Boolean value and error string
            if failed or None if successful
        """
        try:
            db.session.commit()

        except Exception as e:
            db.session.rollback()
            db.session.remove()

            logger.warning(
                f"Skipping item {job_obj.id} due to database drop: {e}"
            )
            return False, str(e)

        return True, None

    @classmethod
    def create_job(cls, report_type: str) -> Job:
        """
        Creates a new job order.

        Args:
            report_type: the type of report

        Returns:
            Job: the Job object that was just added to the database.
        """
        new_job = Job(report_type=report_type)

        try:
            db.session.add(new_job)
            db.session.commit()

        except IntegrityError as e:

            logger.error(f"Unable to save report: {e}")

            db.session.rollback()
            raise ValueError("Unable to save report.")

        return new_job