from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
from dotenv import load_dotenv
import os
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
import requests
import json
import secrets
import string
from datetime import datetime
from dotenv import load_dotenv
from modeles.role import ROLE
from modeles.department import Department
from namespace.GameNamespace import GameNamespace
from namespace.MeetingNamespace import MeetingNamespace
from flask_cors import CORS
from flask_socketio import SocketIO, emit, Namespace
import socketio

load_dotenv()
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Single SocketIO instance with multiple namespaces
socketio_app = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Separate connection dictionaries for each namespace
client_connections_game = {} 
client_connections_meeting = {}

# Server configurations
AUTH_server = os.getenv('AUTH_SERVER')
SAVING_server = os.getenv('SAVING_server')
UserServices = os.getenv('UserServices_server')
Game_server = os.getenv('Game_server')
Meet_server = os.getenv('Meet_server')

app.secret_key = 'your-super-secret-jwt-token-with-at-least-32-characters-long'

jwt = JWTManager(app)

# =================== HELPER FUNCTIONS ===================

def get_user_email_from_jwt_identity(user_id):
    """
    Get user email from auth service using the JWT identity (user ID).
    This function is used whenever we need to resolve the user email from the JWT token.
    
    Args:
        user_id: The user ID extracted from JWT token using get_jwt_identity()
    
    Returns:
        str: User email if found, None otherwise
    """
    try:
        response = requests.get(
            f'http://{AUTH_server}/user/{user_id}/email',
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("email")
        else:
            print(f"Failed to get user email: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting user email from auth service: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error getting user email: {e}")
        return None

def create_GameServer_connection(client_sid, namespace_instance):
    """Create a dedicated backend connection for a game client"""
    backend = socketio.Client(logger=False, engineio_logger=False)
    
    @backend.on('matchCreated')
    def on_match_created(data):
        print(f"Backend -> Client {client_sid}: matchCreated {data}")
        socketio_app.emit('matchCreated', data, to=client_sid, namespace='/game')
    
    @backend.on('matchJoined')
    def on_match_joined(data):
        print(f"Backend -> Client {client_sid}: matchJoined {data}")
        socketio_app.emit('matchJoined', data, to=client_sid, namespace='/game')
    
    @backend.on('gameState')
    def on_game_state(data):
        print(f"Backend -> Client {client_sid}: gameState")
        socketio_app.emit('gameState', data, to=client_sid, namespace='/game')
    
    @backend.on('error')
    def on_error(data):
        print(f"Backend -> Client {client_sid}: error {data}")
        socketio_app.emit('error', data, to=client_sid, namespace='/game')
    
    try:
        backend.connect(Game_server)
        print(f"✅ Created backend connection for game client {client_sid}")
        return backend
    except Exception as e:
        print(f"❌ Failed to connect to game backend for client {client_sid}: {e}")
        return None


def create_MeetServer_connection(client_sid, namespace_instance, user_email=None):
    """Create a dedicated backend connection for a meeting client"""
    connection_url = Meet_server
    if user_email:
        connection_url = f"{Meet_server}?user_email={user_email}"
    
    backend = socketio.Client(
        logger=False, 
        engineio_logger=False,
        ssl_verify=False,
        # Fix: Remove invalid parameters and use correct ones
        reconnection=True,
        reconnection_attempts=5,
        reconnection_delay=1,
        reconnection_delay_max=5,
        # Remove these invalid parameters:
        # ping_timeout=60000,
        # ping_interval=25000
    )
    
    @backend.on('room-joined')
    def on_room_joined(data):
        print(f"Backend -> Client {client_sid}: room-joined")
        socketio_app.emit('room-joined', data, to=client_sid, namespace='/meeting')
    
    @backend.on('new-peer')
    def on_new_peer(data):
        print(f"Backend -> Client {client_sid}: new-peer {data.get('peerId')}")
        socketio_app.emit('new-peer', data, to=client_sid, namespace='/meeting')
    
    @backend.on('peer-disconnected')
    def on_peer_disconnected(data):
        print(f"Backend -> Client {client_sid}: peer-disconnected {data.get('peerId')}")
        socketio_app.emit('peer-disconnected', data, to=client_sid, namespace='/meeting')
    
    @backend.on('offer')
    def on_offer(data):
        print(f"Backend -> Client {client_sid}: offer from {data.get('peerId')}")
        socketio_app.emit('offer', data, to=client_sid, namespace='/meeting')
    
    @backend.on('answer')
    def on_answer(data):
        print(f"Backend -> Client {client_sid}: answer from {data.get('peerId')}")
        socketio_app.emit('answer', data, to=client_sid, namespace='/meeting')
    
    @backend.on('ice-candidate')
    def on_ice_candidate(data):
        print(f"Backend -> Client {client_sid}: ice-candidate from {data.get('peerId')}")
        socketio_app.emit('ice-candidate', data, to=client_sid, namespace='/meeting')
    
    @backend.on('error')
    def on_error(data):
        print(f"Backend -> Client {client_sid}: error {data}")
        socketio_app.emit('error', data, to=client_sid, namespace='/meeting')
    
    @backend.on('room-full')
    def on_room_full(data):
        print(f"Backend -> Client {client_sid}: room-full")
        socketio_app.emit('room-full', data, to=client_sid, namespace='/meeting')
    
    try:
        backend.connect(connection_url)
        print(f"✅ Created backend connection for meeting client {client_sid}")
        return backend
    except Exception as e:
        print(f"❌ Failed to connect to meeting backend for client {client_sid}: {e}")
        return None

# Register namespaces
socketio_app.on_namespace(GameNamespace('/game', socketio_app, Game_server))
socketio_app.on_namespace(MeetingNamespace('/meeting', socketio_app, Meet_server))


# =================== HTTP ENDPOINTS ===================

# Health check endpoints
@app.route('/health', methods=['GET'])
def health():
    """Kubernetes health check endpoint"""
    health_status = {
        "status": "healthy",
        "service": "gateway",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "pod_name": os.getenv('POD_NAME', 'unknown'),
        "pod_ip": os.getenv('POD_IP', 'unknown'),
    }
    
    check_type = request.headers.get('X-Health-Check', 'general')
    
    if check_type == 'readiness':
        downstream_services = {
            'auth-service': AUTH_server,
            'user-service': UserServices,
            'saving-service': SAVING_server
        }
        
        services_status = {}
        all_healthy = True
        
        for service_name, service_url in downstream_services.items():
            try:
                response = requests.get(f"{service_url}/health", timeout=2)
                services_status[service_name] = {
                    'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                    'response_time': response.elapsed.total_seconds()
                }
            except Exception as e:
                services_status[service_name] = {
                    'status': 'unreachable',
                    'error': str(e)
                }
                all_healthy = False
        
        health_status['downstream_services'] = services_status
        health_status['status'] = 'healthy' if all_healthy else 'degraded'
        
        if not all_healthy:
            return jsonify(health_status), 503
    
    return jsonify(health_status), 200


@app.route('/ready', methods=['GET'])
def ready():
    """Simple readiness check"""
    return jsonify({"status": "ready"}), 200


@app.route('/live', methods=['GET'])
def live():
    """Simple liveness check"""
    return jsonify({"status": "alive"}), 200


@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus metrics endpoint"""
    return """# HELP gateway_requests_total Total requests
# TYPE gateway_requests_total counter
gateway_requests_total 0
""", 200, {'Content-Type': 'text/plain'}


# Authentication endpoints
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    print(email, password)
    
    if (email is None) or (password is None):
        return jsonify({"Text": "missing content"}), 401
    else:
        return requests.post(f'http://{AUTH_server}/login', json=data).json(), 200


@app.route('/signup', methods=['POST'])
def signUp():
    data = request.get_json()

    email = data.get('email')
    firstName = data.get('FirstName')
    lastName = data.get('LastName')
    Password = data.get('Password')
    DateOfBirth = data.get('DateOfBirth')
    address = data.get('Address')
    ManagerCode = data.get('managercode')
    
    if not all([email, firstName, lastName, Password, DateOfBirth, address]):
        return jsonify({"Text": "Missing required fields"}), 400
    
    response_from_auth_service = requests.post(f'http://{AUTH_server}/signup', json={
        "email": email,
        "Password": Password,
        "FirstName": firstName,
        "LastName": lastName,
        "DateOfBirth": DateOfBirth,
        "Address": address,
        "managercode": ManagerCode
    })

    if response_from_auth_service.status_code == 200:
            auth_data = response_from_auth_service.json()
        
        # Fix: Remove the curly braces around .get("Token")
            return jsonify({
            "AuthToken": auth_data.get("Token"),
            "id": auth_data.get("id"),
            "firstname":firstName,
            "lastname":lastName,
            "role":"employee"
        }), 200
    else:
        return jsonify({"error": "we get an error from auth service"}), 500


@app.route('/getCodeForManager', methods=['GET'])
@jwt_required()
def getCode():
    """Gateway endpoint - forwards request to UserServices"""
    try:
        #current_user_email = get_jwt_identity()#hadi twali ta5edhha ml authservice
        
        manager_email = get_user_email_from_jwt_identity(get_jwt_identity())
        print(manager_email)
        if not manager_email:
            return jsonify({"Text": "Manager email is required"}), 400
        print ("lhan labes")
        response = requests.post(
            f'http://{UserServices}/getCodeForManager',
            json={
    #            "current_user_email": current_user_email,
                "manager_email": manager_email
            },
            timeout=10
        )
        
        return response.json(), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({"Text": f"Service communication error: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"Text": f"Internal error: {str(e)}"}), 500


# Teammates endpoints
@app.route('/teammates', methods=['GET'])
@jwt_required()
def get_teammates():
    """
    Gateway endpoint - Get teammates for the currently logged-in user.
    Uses JWT identity to determine the user's email.
    
    Query Parameters:
        - include_details (bool): If true, returns full user objects instead of just emails
        - include_manager (bool): If true, includes manager information in response
    """
    try:
        # Get current user's email from JWT
        current_user_email = get_user_email_from_jwt_identity(get_jwt_identity())
        
        if not current_user_email:
            return jsonify({"success": False, "error": "Could not determine user email from token"}), 401
        
        # Get query parameters
        include_details = request.args.get('include_details', 'true')
        include_manager = request.args.get('include_manager', 'true')
        
        # Forward request to UserServices
        response = requests.get(
            f'http://{UserServices}/users/{current_user_email}/teammates',
            params={
                'include_details': include_details,
                'include_manager': include_manager
            },
            timeout=10
        )
        
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": f"Service communication error: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"success": False, "error": f"Internal error: {str(e)}"}), 500


@app.route('/team', methods=['GET'])
@jwt_required()
def get_full_team():
    """
    Gateway endpoint - Get full team information for the currently logged-in user.
    Uses JWT identity to determine the user's email.
    
    Returns full team info including the employee, their manager, and all teammates with details.
    """
    try:
        # Get current user's email from JWT
        current_user_email = get_user_email_from_jwt_identity(get_jwt_identity())
        
        if not current_user_email:
            return jsonify({"success": False, "error": "Could not determine user email from token"}), 401
        
        # Forward request to UserServices
        response = requests.get(
            f'http://{UserServices}/users/{current_user_email}/team',
            timeout=10
        )
        
        return jsonify(response.json()), response.status_code
        
    except requests.exceptions.RequestException as e:
        return jsonify({"success": False, "error": f"Service communication error: {str(e)}"}), 503
    except Exception as e:
        return jsonify({"success": False, "error": f"Internal error: {str(e)}"}), 500


# Meeting endpoints
@app.route('/create-meet', methods=['POST'])
@jwt_required()
def create_meet():
    print(jwt)
    """Forward create-meet request to backend"""
    try:
        print(get_jwt_identity())
        print("Forwarding create-meet request to backend")
        response = requests.post(
            f"{Meet_server}/create-meet",
            json=request.json,
            verify=False
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Error forwarding create-meet: {e}")
        return jsonify({"error": "Gateway error"}), 500


@app.route('/join-meet', methods=['POST'])
def join_meet():
    """Forward join-meet request to backend"""
    try:
        print("Forwarding join-meet request to backend")
        response = requests.post(
            f"{Meet_server}/join-meet",
            json=request.json,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            if 'redirectUrl' in data:
                original_url = data['redirectUrl']
                path = original_url.split('/', 3)[-1] if '/' in original_url else ''
                data['redirectUrl'] = f"https://localhost:7050/{path}"
            return jsonify(data), response.status_code
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Error forwarding join-meet: {e}")
        return jsonify({"error": "Gateway error"}), 500


@app.route('/room/<meet_id>/<user_email>')
def room(meet_id, user_email):
    """Forward room page request to backend"""
    try:
        print(f"Forwarding room request for {meet_id}/{user_email}")
        response = requests.get(
            f"{Meet_server}/room/{meet_id}/{user_email}",
            verify=False
        )
        
        if response.status_code == 200:
            html_content = response.text
            html_content = html_content.replace(
                'server="https://{Meet_server}:7053"',
                'server="https://localhost:7050"'
            )
            return html_content, 200
        else:
            return response.text, response.status_code
            
    except Exception as e:
        print(f"Error forwarding room request: {e}")
        return "Gateway error", 500

# user service 
@app.route('/becamemanager', methods=['POST'])
@jwt_required()
def becameManager():
    user_id = get_jwt_identity()
    userMail = get_user_email_from_jwt_identity(user_id)
    
    if userMail is None:
        return jsonify({"error": "Could not resolve user identity"}), 401
    
    print("user to became manager : ", userMail)
    code = (request.get_json()).get("code")
    response = requests.post(
        f"http://{UserServices}/becameManger",
        json={"code": code, "userMail": userMail}
    )
    print("el response : ", response.json())
    return response.json(), response.status_code
    
@app.route('/generateBecameManagerCode', methods=['GET'])
def generate_became_manager_code():
    try:
        data = request.get_json()
        response = requests.get(
            f'http://{UserServices}/generateBecameManagerCode',
            json=data,
            timeout=10
        )
        return response.json(), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/user/identity', methods=['GET'])
@jwt_required()
def get_user_identity():
    """
    Get the current user's identity (email) from JWT token.
    This endpoint demonstrates how to resolve user email from JWT identity.
    """
    try:
        user_id = get_jwt_identity()
        user_email = get_user_email_from_jwt_identity(user_id)
        
        if user_email is None:
            return jsonify({"error": "Could not resolve user identity"}), 404
        
        return jsonify({
            "user_id": user_id,
            "email": user_email
        }), 200
    except Exception as e:
        print(f"Error getting user identity: {e}")
        return jsonify({"error": "Error retrieving user identity"}), 500



# =================== NEW MEETING CRUD ENDPOINTS ===================

@app.route('/meetings', methods=['GET'])
@jwt_required()
def get_all_meetings():
    """Forward get all meetings request to backend"""
    try:
        user_email = request.args.get('user_email')
        is_active = request.args.get('is_active')
        
        params = {}
        if user_email:
            params['user_email'] = user_email
        if is_active:
            params['is_active'] = is_active
        
        response = requests.get(
            f"{Meet_server}/meetings",
            params=params,
            verify=False
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Error forwarding get meetings: {e}")
        return jsonify({"error": "Gateway error"}), 500


@app.route('/meetings/<meeting_id>', methods=['GET'])
@jwt_required()
def get_meeting(meeting_id):
    """Forward get meeting by ID request to backend"""
    try:
        response = requests.get(
            f"{Meet_server}/meetings/{meeting_id}",
            verify=False
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Error forwarding get meeting: {e}")
        return jsonify({"error": "Gateway error"}), 500


@app.route('/meetings/<meeting_id>', methods=['PUT'])
@jwt_required()
def update_meeting(meeting_id):
    """Forward update meeting request to backend"""
    try:
        response = requests.put(
            f"{Meet_server}/meetings/{meeting_id}",
            json=request.json,
            verify=False
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Error forwarding update meeting: {e}")
        return jsonify({"error": "Gateway error"}), 500


@app.route('/meetings/<meeting_id>', methods=['DELETE'])
@jwt_required()
def delete_meeting(meeting_id):
    """Forward delete meeting request to backend"""
    try:
        response = requests.delete(
            f"{Meet_server}/meetings/{meeting_id}",
            verify=False
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Error forwarding delete meeting: {e}")
        return jsonify({"error": "Gateway error"}), 500


@app.route('/meetings/<meeting_id>/start', methods=['POST'])
@jwt_required()
def start_meeting(meeting_id):
    """Forward start meeting request to backend"""
    try:
        response = requests.post(
            f"{Meet_server}/meetings/{meeting_id}/start",
            verify=False
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Error forwarding start meeting: {e}")
        return jsonify({"error": "Gateway error"}), 500


@app.route('/meetings/<meeting_id>/end', methods=['POST'])
@jwt_required()
def end_meeting(meeting_id):
    """Forward end meeting request to backend"""
    try:
        response = requests.post(
            f"{Meet_server}/meetings/{meeting_id}/end",
            verify=False
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Error forwarding end meeting: {e}")
        return jsonify({"error": "Gateway error"}), 500


@app.route('/meetings/<meeting_id>/log', methods=['POST'])
@jwt_required()
def add_meeting_log(meeting_id):
    """Forward add log entry request to backend"""
    try:
        response = requests.post(
            f"{Meet_server}/meetings/{meeting_id}/log",
            json=request.json,
            verify=False
        )
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Error forwarding add log entry: {e}")
        return jsonify({"error": "Gateway error"}), 500


@app.route('/meetings/<meeting_id>/log', methods=['GET'])
@jwt_required()
def get_meeting_log(meeting_id):
    """Forward get meeting log request to backend"""
    try:
        download = request.args.get('download')
        params = {}
        if download:
            params['download'] = download
        
        response = requests.get(
            f"{Meet_server}/meetings/{meeting_id}/log",
            params=params,
            verify=False
        )
        
        if download and response.status_code == 200:
            # Forward the file download response
            return response.content, response.status_code, response.headers.items()
        else:
            return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"Error forwarding get meeting log: {e}")
        return jsonify({"error": "Gateway error"}), 500


if __name__ == '__main__':
    socketio_app.run(app, host='0.0.0.0', port=7050, debug=True, allow_unsafe_werkzeug=True,ssl_context=('meetingService\\certifs\\cert.pem', 'meetingService\\certifs\\key.pem'))