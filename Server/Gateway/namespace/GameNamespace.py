from flask_socketio import Namespace
from flask import request
import socketio


class GameNamespace(Namespace):
    """Namespace for game-related WebSocket events"""
    
    def __init__(self, namespace, socketio_app, game_server_url):
        super().__init__(namespace)
        self.socketio_app = socketio_app
        self.game_server_url = game_server_url
        self.client_connections = {}
    
    def create_backend_connection(self, client_sid):
        """Create a dedicated backend connection for a game client"""
        backend = socketio.Client(logger=False, engineio_logger=False)
        
        @backend.on('matchCreated')
        def on_match_created(data):
            print(f"Backend -> Client {client_sid}: matchCreated {data}")
            self.socketio_app.emit('matchCreated', data, to=client_sid, namespace='/game')
        
        @backend.on('matchJoined')
        def on_match_joined(data):
            print(f"Backend -> Client {client_sid}: matchJoined {data}")
            self.socketio_app.emit('matchJoined', data, to=client_sid, namespace='/game')
        
        @backend.on('gameState')
        def on_game_state(data):
            print(f"Backend -> Client {client_sid}: gameState")
            self.socketio_app.emit('gameState', data, to=client_sid, namespace='/game')
        
        @backend.on('error')
        def on_error(data):
            print(f"Backend -> Client {client_sid}: error {data}")
            self.socketio_app.emit('error', data, to=client_sid, namespace='/game')
        
        try:
            backend.connect(self.game_server_url)
            print(f"✅ Created backend connection for game client {client_sid}")
            return backend
        except Exception as e:
            print(f"❌ Failed to connect to game backend for client {client_sid}: {e}")
            return None
    
    def on_connect(self, auth=None):
        """Client connected to game namespace"""
        client_sid = request.sid
        print(f"✅ Game Client connected: {client_sid}")
        
        backend = self.create_backend_connection(client_sid)
        if backend:
            self.client_connections[client_sid] = backend
        else:
            self.emit('error', 'Failed to connect to game server', to=client_sid)
    
    def on_disconnect(self):
        """Client disconnected from game namespace"""
        client_sid = request.sid
        print(f"❌ Game Client disconnected: {client_sid}")
        
        if client_sid in self.client_connections:
            try:
                self.client_connections[client_sid].disconnect()
            except Exception as e:
                print(f"Error disconnecting game backend: {e}")
            del self.client_connections[client_sid]
    
    def on_createMatch(self):
        """Forward createMatch to backend"""
        client_sid = request.sid
        print(f"Client {client_sid} -> Backend: createMatch")
        
        if client_sid in self.client_connections:
            self.client_connections[client_sid].emit('createMatch')
        else:
            self.emit('error', 'Backend connection not found', to=client_sid)
    
    def on_joinMatch(self, match_code):
        """Forward joinMatch to backend"""
        client_sid = request.sid
        print(f"Client {client_sid} -> Backend: joinMatch {match_code}")
        
        if client_sid in self.client_connections:
            self.client_connections[client_sid].emit('joinMatch', match_code)
        else:
            self.emit('error', 'Backend connection not found', to=client_sid)
    
    def on_makeMove(self, data):
        """Forward makeMove to backend"""
        client_sid = request.sid
        print(f"Client {client_sid} -> Backend: makeMove")
        
        if client_sid in self.client_connections:
            self.client_connections[client_sid].emit('makeMove', data)
        else:
            self.emit('error', 'Backend connection not found', to=client_sid)
    
    def on_restartGame(self, match_code):
        """Forward restartGame to backend"""
        client_sid = request.sid
        print(f"Client {client_sid} -> Backend: restartGame {match_code}")
        
        if client_sid in self.client_connections:
            self.client_connections[client_sid].emit('restartGame', match_code)
        else:
            self.emit('error', 'Backend connection not found', to=client_sid)