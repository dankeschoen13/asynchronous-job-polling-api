import time
from datetime import datetime
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
            print(f"\n--- Found {len(pending_jobs)} pending job(s) in queue ---")

            for job in pending_jobs:
                current_time = datetime.now().strftime("%H:%M:%S")
                print(f"[{current_time}] Claiming Job {job.id}...")

                # 1. Lock it as processing immediately
                job.status = TicketStatus.PROCESSING
                success, error_msg = JobSvc.save_changes(job)

                if error_msg:
                    print(f"[ERROR] Failed to lock Job {job.id}: {error_msg}")
                    continue

                print(
                    f"[{datetime.now().strftime('%H:%M:%S')}] Job {job.id} locked. Simulating 10-second heavy processing...")
                # 2. Place-holder work
                time.sleep(10)

                # 3. The Delivery
                job.status = TicketStatus.COMPLETED
                job.download_url = f"https://fake-job-order.com/downloads/report/{job.id}"
                success, error_msg = JobSvc.save_changes(job)

                if error_msg:
                    print(f"[ERROR] Failed to save completed Job {job.id}: {error_msg}")
                    continue

                print(f"[{datetime.now().strftime('%H:%M:%S')}] Job {job.id} successfully COMPLETED.")
        else:
            # Keeps the terminal quiet while polling
            time.sleep(2)