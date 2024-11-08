from flask import Flask, jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from dotenv import load_dotenv
import os

from config import CORS_ORIGINS, RATE_LIMIT
from routes import create_pnr_status_routes
from logging_config import setup_logging

load_dotenv()
setup_logging()

app = Flask(__name__)

CORS(app, resources={
    r"/api/*": {
        "origins": CORS_ORIGINS,
        "methods": ["GET", "POST"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[RATE_LIMIT]
)

# Register Blueprints
pnr_status_blueprint = create_pnr_status_routes(limiter)
app.register_blueprint(pnr_status_blueprint, url_prefix='/api')

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the PNR Status API"})

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "An internal server error occurred. Please try again later."}), 500

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 4000))
    app.run(host="0.0.0.0", port=port, debug=True)
