from flask import Flask, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import socketio

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Gateway SocketIO server (facing clients)
gateway_io = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Store separate backend connections for each client
client_connections_Game = {}  # {gateway_client_sid: backend_socketio_client}

Game_server = 'http://localhost:3000'


def create_backend_connection(client_sid):
    """Create a dedicated backend connection for a client"""
    backend = socketio.Client(logger=False, engineio_logger=False)
    
    # Setup event handlers for this specific backend connection
    @backend.on('matchCreated')
    def on_match_created(data):
        print(f"Backend -> Client {client_sid}: matchCreated {data}")
        gateway_io.emit('matchCreated', data, to=client_sid)
    
    @backend.on('matchJoined')
    def on_match_joined(data):
        print(f"Backend -> Client {client_sid}: matchJoined {data}")
        gateway_io.emit('matchJoined', data, to=client_sid)
    
    @backend.on('gameState')
    def on_game_state(data):
        print(f"Backend -> Client {client_sid}: gameState")
        gateway_io.emit('gameState', data, to=client_sid)
    
    @backend.on('error')
    def on_error(data):
        print(f"Backend -> Client {client_sid}: error {data}")
        gateway_io.emit('error', data, to=client_sid)
    
    try:
        backend.connect(Game_server)
        print(f"✅ Created backend connection for client {client_sid}")
        return backend
    except Exception as e:
        print(f"❌ Failed to connect to backend for client {client_sid}: {e}")
        return None


# ============= CLIENT EVENT HANDLERS =============

@gateway_io.on('connect')
def handle_client_connect():
    """Client connected to gateway - create dedicated backend connection"""
    client_sid = request.sid
    print(f"✅ Client connected: {client_sid}")
    
    # Create a dedicated backend connection for this client
    backend = create_backend_connection(client_sid)
    if backend:
        client_connections_Game[client_sid] = backend
    else:
        emit('error', 'Failed to connect to game server')


@gateway_io.on('disconnect')
def handle_client_disconnect():
    """Client disconnected - cleanup backend connection"""
    client_sid = request.sid
    print(f"❌ Client disconnected: {client_sid}")
    
    # Disconnect and cleanup backend connection
    if client_sid in client_connections_Game:
        try:
            client_connections_Game[client_sid].disconnect()
        except:
            pass
        del client_connections_Game[client_sid]


@gateway_io.on('createMatch')
def handle_create_match():
    """Forward createMatch to backend"""
    client_sid = request.sid
    print(f"Client {client_sid} -> Backend: createMatch")
    
    if client_sid in client_connections_Game:
        client_connections_Game[client_sid].emit('createMatch')


@gateway_io.on('joinMatch')
def handle_join_match(match_code):
    """Forward joinMatch to backend"""
    client_sid = request.sid
    print(f"Client {client_sid} -> Backend: joinMatch {match_code}")
    
    if client_sid in client_connections_Game:
        client_connections_Game[client_sid].emit('joinMatch', match_code)


@gateway_io.on('makeMove')
def handle_make_move(data):
    """Forward makeMove to backend"""
    client_sid = request.sid
    print(f"Client {client_sid} -> Backend: makeMove")
    
    if client_sid in client_connections_Game:
        client_connections_Game[client_sid].emit('makeMove', data)


@gateway_io.on('restartGame')
def handle_restart_game(match_code):
    """Forward restartGame to backend"""
    client_sid = request.sid
    print(f"Client {client_sid} -> Backend: restartGame {match_code}")
    
    if client_sid in client_connections_Game:
        client_connections_Game[client_sid].emit('restartGame', match_code)


@app.route('/health')
def health_check():
    """Health check endpoint"""
    active_connections = len(client_connections_Game)
    connected_backends = sum(1 for c in client_connections_Game.values() if c.connected)
    
    return {
        "status": "ok",
        "gateway": "running",
        "active_clients": active_connections,
        "connected_backends": connected_backends
    }


if __name__ == '__main__':
    print("🚀 Starting Flask Gateway Server...")
    print(f"📡 Backend server: {Game_server}")
    print(f"🌐 Gateway listening on port 5000")
    
    gateway_io.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)