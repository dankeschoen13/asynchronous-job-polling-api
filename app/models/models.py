from sqlalchemy import String, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.extensions import db
from datetime import datetime, timezone
import enum

class TicketStatus(str, enum.Enum):
    PENDING = "Pending"
    PROCESSING = "Processing"
    COMPLETED = "Completed"
    FAILED = "Failed"

class Job(db.Model):
    __tablename__ = 'jobs'
    id: Mapped[int] = mapped_column(primary_key=True)
    report_type: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, name="ticket_status_enum", create_constraint=True),
        default=TicketStatus.PENDING,
        server_default="PENDING",
        nullable=False
    )
    download_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )
    date_submitted: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False
    )
    date_updated: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
        nullable=False
    )
