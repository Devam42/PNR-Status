from flask import Blueprint, request, jsonify
import re
import time

from utils import get_data, extract_data

pnr_status_blueprint = Blueprint('pnr_status', __name__)

def create_pnr_status_routes(limiter):
    @pnr_status_blueprint.route('/pnr-status', methods=['GET'])
    @limiter.limit("120 per minute")
    def pnr_status():
        try:
            pnr_number = request.args.get('pnrNumber')
            if not pnr_number or not re.match(r'^\d{10}$', pnr_number):
                return jsonify({"error": "Invalid PNR format. It must be a 10-digit number."}), 400

            url = f"https://www.confirmtkt.com/pnr-status/{pnr_number}"
            html_data, error = get_data(url)
            if error:
                return jsonify({"error": error}), 500
            if not html_data:
                return jsonify({"error": "Failed to retrieve data from the server"}), 500

            extracted_data = extract_data(html_data, pnr_number)
            if "error" in extracted_data:
                return jsonify({"error": extracted_data["error"]}), 500

            # Wrap the data in the desired response format
            response = {
                "status": True,
                "message": "Success",
                "timestamp": int(time.time() * 1000),
                "data": extracted_data
            }

            return jsonify(response)
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return pnr_status_blueprint
