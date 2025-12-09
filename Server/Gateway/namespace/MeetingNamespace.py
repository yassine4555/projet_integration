from flask_socketio import Namespace
from flask import request
import socketio


class MeetingNamespace(Namespace):
    """Namespace for meeting/video conference WebSocket events"""
    
    def __init__(self, namespace, socketio_app, meet_server_url):
        super().__init__(namespace)
        self.socketio_app = socketio_app
        self.meet_server_url = meet_server_url
        self.client_connections = {}
    
    def create_backend_connection(self, client_sid, user_email=None):
        """Create a dedicated backend connection for a meeting client"""
        connection_url = self.meet_server_url
        if user_email:
            connection_url = f"{self.meet_server_url}?user_email={user_email}"
        
        backend = socketio.Client(
            logger=False, 
            engineio_logger=False,
            ssl_verify=False,
            reconnection=True,
            reconnection_attempts=5,
            reconnection_delay=1,
            reconnection_delay_max=5,
        )
        
        @backend.on('room-joined')
        def on_room_joined(data):
            print(f"Backend -> Client {client_sid}: room-joined")
            self.socketio_app.emit('room-joined', data, to=client_sid, namespace='/meeting')
        
        @backend.on('new-peer')
        def on_new_peer(data):
            print(f"Backend -> Client {client_sid}: new-peer {data.get('peerId')}")
            self.socketio_app.emit('new-peer', data, to=client_sid, namespace='/meeting')
        
        @backend.on('peer-disconnected')
        def on_peer_disconnected(data):
            print(f"Backend -> Client {client_sid}: peer-disconnected {data.get('peerId')}")
            self.socketio_app.emit('peer-disconnected', data, to=client_sid, namespace='/meeting')
        
        @backend.on('offer')
        def on_offer(data):
            print(f"Backend -> Client {client_sid}: offer from {data.get('peerId')}")
            self.socketio_app.emit('offer', data, to=client_sid, namespace='/meeting')
        
        @backend.on('answer')
        def on_answer(data):
            print(f"Backend -> Client {client_sid}: answer from {data.get('peerId')}")
            self.socketio_app.emit('answer', data, to=client_sid, namespace='/meeting')
        
        @backend.on('ice-candidate')
        def on_ice_candidate(data):
            print(f"Backend -> Client {client_sid}: ice-candidate from {data.get('peerId')}")
            self.socketio_app.emit('ice-candidate', data, to=client_sid, namespace='/meeting')
        
        @backend.on('error')
        def on_error(data):
            print(f"Backend -> Client {client_sid}: error {data}")
            self.socketio_app.emit('error', data, to=client_sid, namespace='/meeting')
        
        @backend.on('room-full')
        def on_room_full(data):
            print(f"Backend -> Client {client_sid}: room-full")
            self.socketio_app.emit('room-full', data, to=client_sid, namespace='/meeting')
        
        try:
            backend.connect(connection_url)
            print(f"✅ Created backend connection for meeting client {client_sid}")
            return backend
        except Exception as e:
            print(f"❌ Failed to connect to meeting backend for client {client_sid}: {e}")
            return None
    
    def on_connect(self, auth=None):
        """Client connected to meeting namespace"""
        client_sid = request.sid
        user_email = request.args.get('user_email')
        print(f"✅ Meeting Client connected: {client_sid} (email: {user_email})")
        
        backend = self.create_backend_connection(client_sid, user_email)
        if backend:
            self.client_connections[client_sid] = {
                'backend': backend,
                'user_email': user_email
            }
        else:
            self.emit('error', 'Failed to connect to meeting server', to=client_sid)
    
    def on_disconnect(self):
        """Client disconnected from meeting namespace"""
        client_sid = request.sid
        print(f"❌ Meeting Client disconnected: {client_sid}")
        
        if client_sid in self.client_connections:
            try:
                self.client_connections[client_sid]['backend'].disconnect()
            except Exception as e:
                print(f"Error disconnecting meeting backend: {e}")
            del self.client_connections[client_sid]
    
    def on_join(self, data):
        """Forward join event to backend"""
        client_sid = request.sid
        print(f"Client {client_sid} -> Backend: join room {data.get('room')}")
        
        if client_sid in self.client_connections:
            self.client_connections[client_sid]['backend'].emit('join', data)
        else:
            self.emit('error', 'Backend connection not found', to=client_sid)
    
    def on_leave(self, data):
        """Forward leave event to backend"""
        client_sid = request.sid
        print(f"Client {client_sid} -> Backend: leave room {data.get('room')}")
        
        if client_sid in self.client_connections:
            self.client_connections[client_sid]['backend'].emit('leave', data)
        else:
            self.emit('error', 'Backend connection not found', to=client_sid)
    
    def on_offer(self, data):
        """Forward WebRTC offer to backend"""
        client_sid = request.sid
        print(f"Client {client_sid} -> Backend: offer to {data.get('targetId')}")
        
        if client_sid in self.client_connections:
            self.client_connections[client_sid]['backend'].emit('offer', data)
        else:
            self.emit('error', 'Backend connection not found', to=client_sid)
    
    def on_answer(self, data):
        """Forward WebRTC answer to backend"""
        client_sid = request.sid
        print(f"Client {client_sid} -> Backend: answer to {data.get('targetId')}")
        
        if client_sid in self.client_connections:
            self.client_connections[client_sid]['backend'].emit('answer', data)
        else:
            self.emit('error', 'Backend connection not found', to=client_sid)
    
    def on_ice_candidate(self, data):
        """Forward ICE candidate to backend"""
        client_sid = request.sid
        print(f"Client {client_sid} -> Backend: ice-candidate to {data.get('targetId')}")
        
        if client_sid in self.client_connections:
            self.client_connections[client_sid]['backend'].emit('ice-candidate', data)
        else:
            self.emit('error', 'Backend connection not found', to=client_sid)