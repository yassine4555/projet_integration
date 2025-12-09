from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from dotenv import load_dotenv
import os
from Helper import FileHelper
from io import BytesIO

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Initialize the file helper
file_helper = FileHelper()

# Internal API key for gateway authentication
INTERNAL_API_KEY = "INTERNAL_API_KEY"


def verify_internal_request():
    """Verify that the request comes from the gateway"""
    api_key = request.headers.get('X-Internal-Key')
    return api_key == INTERNAL_API_KEY


@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Upload a file to the saving server
    Expects:
        - file in the request files
        - user_email in the request headers (sent by gateway)
    """
    # Verify internal request
    #if not verify_internal_request():
    #    return jsonify({"error": "Unauthorized"}), 401
    #
    ## Get user email from headers (sent by gateway from JWT)
    #user_email = request.headers.get('X-User-Email')
    #if not user_email:
    #    return jsonify({"error": "User email not provided"}), 400
    #
    ## Check if file is in request
    #if 'file' not in request.files:
    #    return jsonify({"error": "No file provided"}), 400
    user_email="manager@mas3oud.tcom"
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    # Upload file using helper
    result = file_helper.upload_file(file, user_email)
    
    if result['success']:
        return jsonify({
            "message": "File uploaded successfully",
            "data": result['data']
        }), 200
    else:
        return jsonify({
            "error": "Failed to upload file",
            "details": result.get('error', result.get('data'))
        }), result['status_code']


@app.route('/getAllfiles', methods=['GET'])
def get_all_files():
    """
    Get all file names from the saving server
    """
    # Verify internal request
    #if not verify_internal_request():
    #    return jsonify({"error": "Unauthorized"}), 401
    
    # Get all files using helper
    result = file_helper.get_all_files()
    
    if result['success']:
        return jsonify({
            "message": "Files retrieved successfully",
            "files": result['data']
        }), 200
    else:
        return jsonify({
            "error": "Failed to retrieve files",
            "details": result.get('error', result.get('data'))
        }), result['status_code']


@app.route('/file/get/<filename>', methods=['GET'])
def get_file(filename):
    """
    Get a specific file from the saving server
    """
    # Verify internal request
    if not verify_internal_request():
        return jsonify({"error": "Unauthorized"}), 401
    
    # Get file using helper
    result = file_helper.get_file(filename)
    
    if result['success']:
        # Return the file
        return send_file(
            BytesIO(result['data']),
            mimetype=result['content_type'],
            as_attachment=True,
            download_name=filename
        )
    else:
        return jsonify({
            "error": "Failed to retrieve file",
            "details": result.get('error', result.get('data'))
        }), result['status_code']


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "dataService"}), 200


if __name__ == '__main__':
    port = int(os.getenv('DATA_SERVICE_PORT', 7055))
    app.run(host='0.0.0.0', port=port, debug=True)
