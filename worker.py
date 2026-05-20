import time
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.services import JobSvc
from app.models import TicketStatus

app = create_app()

with app.app_context():
    print("Worker started. Listening for pending jobs...")

    while True:
        pending_jobs = JobSvc.fetch_pending()
        if pending_jobs:
            for job in pending_jobs:

                # 1. Lock it as processing immediately
                job.status = TicketStatus.PROCESSING
                success, error_msg = JobSvc.save_changes(job)

                if error_msg:
                    continue

                # 2. Place-holder work
                time.sleep(10)

                # 3. The Delivery
                job.status = TicketStatus.COMPLETED
                job.download_url = f"https://fake-job-order.com/downloads/report/{job.id}"
                success, error_msg = JobSvc.save_changes(job)

                if error_msg:
                    continue
        else:
            time.sleep(2)



