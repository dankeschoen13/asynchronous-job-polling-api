from app.models import TicketStatus
from app.services import JobSvc

def test_incoming_reports_success(client):
    """
    Test that a valid message is correctly categorized and saved to the DB.
    """

    # API Call
    payload = {"report_type": "annual_fake_report"}
    response = client.post('api/reports', json=payload)

    # Assertions
    assert response.status_code == 202
    assert response.json["ticket_status"] == "Pending"

def test_check_status(client, app):
    """
    Test if check status route correctly returns the current status of a ticket.
    """

    # DB injection
    fake_job = JobSvc.create_job(report_type="test_status_report")
    job_id = fake_job.id

    # API Call
    response = client.get(f'/api/reports/{job_id}')
    data = response.get_json()

    # Assertions
    assert response.status_code == 200
    assert data['ticket_status'] == TicketStatus.PENDING.value
    assert 'download_url' not in data

def test_incoming_reports_missing_key(client):
    """
    Test that a POST request missing the 'report_type' key returns a 400 error.
    """

    # API Call: Payload is missing the required key 'report_type'
    payload = {"wrong_key": "annual_fake_report"}
    response = client.post('api/reports', json=payload)

    # Assertions
    assert response.status_code == 400
    assert "error" in response.json

def test_check_status_not_found(client):
    """
    Test that requesting a non-existent job ID returns a 404 error.
    """

    # API Call: ID 999 does not exist in the isolated test database
    response = client.get('/api/reports/999')

    # Assertions
    assert response.status_code == 404
    assert response.json["error"] == "Job ID does not exist"

def test_check_status_completed(client, app):
    """
    Test that a completed job returns the download URL in the payload.
    """

    # DB injection
    fake_job = JobSvc.create_job(report_type="test_status_report")

    # Manually transition the state for the test
    fake_job.status = TicketStatus.COMPLETED
    fake_job.download_url = f"https://fake-job-order.com/downloads/report/{fake_job.id}"
    JobSvc.save_changes(fake_job)

    # API Call
    response = client.get(f'/api/reports/{fake_job.id}')
    data = response.get_json()

    # Assertions
    assert response.status_code == 200
    assert data['ticket_status'] == TicketStatus.COMPLETED.value
    assert 'download_url' in data
    assert data['download_url'] == fake_job.download_url