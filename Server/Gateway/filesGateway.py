from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from dotenv import load_dotenv
import os
import requests
from io import BytesIO

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# JWT Configuration
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'your-super-secret-jwt-token-with-at-least-32-characters-long')
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'

jwt = JWTManager(app)

# Data Service URL
DATA_SERVICE = os.getenv('DATA_SERVICE', '192.168.100.190:7055')
DATA_SERVICE_URL = f"http://{DATA_SERVICE}"

# Internal API key for service-to-service communication
INTERNAL_API_KEY = "INTERNAL_API_KEY"


@app.route('/upload', methods=['POST'])
#@jwt_required()
def upload_file():
    """
    Gateway endpoint to upload a file
    - Receives file from client
    - Extracts user email from JWT
    - Forwards to dataService
    """
    try:
        print("📥 Upload request received")
        
        # Get user email from JWT (FIXED!)
        user_email = "test@example.com"  # Hardcoded for testing
        # user_email = get_jwt_identity()  # Uncomment when JWT is enabled
        
        print(f"👤 User: {user_email}")
        
        # Check if file is in request
        if 'file' not in request.files:
            print("❌ No file in request")
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        print(f"📄 File received: {file.filename}")
        
        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({"error": "No file selected"}), 400
        
        # Prepare headers with user email and internal API key
        headers = {
            'X-User-Email': user_email,
            'X-Internal-Key': INTERNAL_API_KEY
        }
        
        # FIX: Read file content first, then create a new BytesIO object
        file_content = file.read()
        print(f"📦 File size: {len(file_content)} bytes")
        
        # Create a new file-like object for requests
        file_obj = BytesIO(file_content)
        file_obj.name = file.filename
        
        # Prepare file for forwarding
        files = {
            'file': (file.filename, file_obj, file.content_type or 'application/octet-stream')
        }
        
        print(f"🔄 Forwarding to: {DATA_SERVICE_URL}/upload")
        
        # Forward request to data service
        response = requests.post(
            f"{DATA_SERVICE_URL}/upload",
            files=files,
            headers=headers,
            timeout=30
        )
        
        print(f"✅ Response status: {response.status_code}")
        print(f"📋 Response body: {response.text[:200]}")  # First 200 chars
        
        # Return the response from data service
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection error to data service: {str(e)}")
        return jsonify({
            "error": "Cannot connect to data service",
            "details": str(e),
            "data_service_url": DATA_SERVICE_URL
        }), 503
        
    except requests.exceptions.Timeout as e:
        print(f"❌ Timeout error: {str(e)}")
        return jsonify({
            "error": "Data service timeout",
            "details": str(e)
        }), 504
        
    except Exception as e:
        print(f"❌ Gateway error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Gateway error",
            "details": str(e)
        }), 500


@app.route('/getAllfiles', methods=['GET'])
#@jwt_required()
def get_all_files():
    """
    Gateway endpoint to get all files
    - Requires JWT authentication
    - Forwards to dataService
    """
    try:
        print("📋 Get all files request received")
        
        # Get user email from JWT (for logging/tracking)
        user_email = "test@example.com"
        # user_email = get_jwt_identity()  # Uncomment when JWT is enabled
        
        # Prepare headers with internal API key
        headers = {
            'X-User-Email': user_email,
            'X-Internal-Key': INTERNAL_API_KEY
        }
        
        # Forward request to data service
        response = requests.get(
            f"{DATA_SERVICE_URL}/getAllfiles",
            headers=headers,
            timeout=10
        )
        
        print(f"✅ Response status: {response.status_code}")
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": "Gateway error", "details": str(e)}), 500


@app.route('/file/get/<filename>', methods=['GET'])
#@jwt_required()
def get_file(filename):
    """
    Gateway endpoint to get a specific file
    - Requires JWT authentication
    - Forwards to dataService
    """
    try:
        print(f"📥 Get file request: {filename}")
        
        # Get user email from JWT (for logging/tracking)
        user_email = "test@example.com"
        # user_email = get_jwt_identity()  # Uncomment when JWT is enabled
        
        # Prepare headers with internal API key
        headers = {
            'X-User-Email': user_email,
            'X-Internal-Key': INTERNAL_API_KEY
        }
        
        # Forward request to data service
        response = requests.get(
            f"{DATA_SERVICE_URL}/file/get/{filename}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"✅ File retrieved: {filename}")
            # Return the file
            return send_file(
                BytesIO(response.content),
                mimetype=response.headers.get('Content-Type', 'application/octet-stream'),
                as_attachment=True,
                download_name=filename
            )
        else:
            print(f"❌ File not found: {filename}")
            return jsonify(response.json()), response.status_code
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({"error": "Gateway error", "details": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "filesGateway"}), 200


@app.route('/test', methods=['GET'])
def test():
    """Simple test endpoint"""
    return jsonify({
        "message": "Gateway is working!",
        "data_service": DATA_SERVICE_URL
    }), 200


if __name__ == '__main__':
    print("🚀 Starting Files Gateway on http://0.0.0.0:8000")
    print(f"📡 Data Service URL: {DATA_SERVICE_URL}")
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
