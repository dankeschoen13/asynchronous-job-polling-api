from flask import Blueprint, jsonify, request
from app.models import TicketStatus
from app.services import JobSvc

api_bp = Blueprint('api', __name__)

@api_bp.post('/reports')
def incoming_reports():
    data = request.get_json(silent=True) or {}

    if not data or 'report_type' not in data:
        return jsonify({"error": "Bad Request. Missing or invalid JSON payload"}), 400

    report = data['report_type']

    try:
        new_job = JobSvc.create_job(report_type=report)
    except ValueError:
        return jsonify({"error": "Internal Server Error. Could not save report."}), 500

    return jsonify({
        "status": "accepted",
        "ticket_status": TicketStatus.PENDING.value,
        "job_id": new_job.id
    }), 202

@api_bp.get('/reports/<int:job_id>')
def check_status(job_id):
    existing_ticket = JobSvc.fetch_by_id(job_id)

    if not existing_ticket:
        return jsonify({"error": "Job ID does not exist"}), 404

    status = {"ticket_status": existing_ticket.status.value}
    
    if existing_ticket.status == "Completed":
        status["download_url"] = existing_ticket.download_url

    return jsonify(status)