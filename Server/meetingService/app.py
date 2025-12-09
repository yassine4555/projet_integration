from meeting import Meeting
from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_cors import CORS
from flask import Flask, jsonify, render_template, session, send_from_directory, request, redirect
from dotenv import load_dotenv
from Helper import MeetHelper
import logging
import os

load_dotenv()
app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Socket.IO with explicit CORS settings
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Keep track of users in rooms
rooms = {}

signalingServer = os.getenv("SIGNALING_SERVER")

@app.route("/create-meet", methods=["POST"])
def create_meet():
    """
    Create a new meeting and store it in SAVING_SERVER
    """
    try:
        meet_data = request.json
        
        # Extract data from request
        title = meet_data.get("title")
        obj = meet_data.get("object")
        description = meet_data.get("description")
        invited_employees = meet_data.get("invitedEmployeesList", [])
        password = meet_data.get("password", "")
        created_by = meet_data.get("created_by", "")
        
        # Validate required fields
        if not title or not obj or not description:
            return jsonify({"error": "Title, object, and description are required"}), 400
        
        if not created_by:
            return jsonify({"error": "created_by is required"}), 400
        
        # Create new meeting
        new_meeting = Meeting(
            title=title,
            obj=obj,
            description=description,
            invited_employees=invited_employees,
            password=password,
            created_by=created_by
        )
        
        # Save meeting to SAVING_SERVER via Helper
        created_meeting = MeetHelper.createMeeting(new_meeting)
        
        if not created_meeting:
            return jsonify({"error": "Failed to create meeting in SAVING_SERVER"}), 500
        
        # Return meeting details
        return jsonify({
            "success": True,
            "meeting": {
                "id": created_meeting.getDatabaseID(),
                "meeting_id": created_meeting.getID(),
                "title": created_meeting.getTitle(),
                "object": created_meeting.getObject(),
                "description": created_meeting.getDescription(),
                "invitationLink": created_meeting.getInvitationLink(),
                "log_path": created_meeting.getLogPath(),
                "createdAt": created_meeting.getCreatedAt(),
                "created_by": created_meeting.getCreatedBy(),
                "invitedEmployees": created_meeting.getInvitedEmployeesList(),
                "is_active": created_meeting.getIsActive()
            }
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating meeting: {str(e)}")
        return jsonify({"error": "Failed to create meeting"}), 500

@app.route("/join-meet", methods=["POST"])
def join_meet():
    """
    Join a meeting - verify credentials and add user to participants
    """
    try:
        meet_data = request.json
        meet_id = meet_data.get("meet_id")
        password = meet_data.get("password")
        user_email = meet_data.get("user_email")
        
        if not meet_id or not user_email:
            return jsonify({"error": "meet_id and user_email are required"}), 400
        
        # Verify meeting password
        if not MeetHelper.verifyMeetingPassword(meet_id, password):
            return jsonify({"error": "Invalid credentials"}), 401

        # Add user to meeting and log the event
        MeetHelper.addUserToMeeting(meet_id, user_email)
        MeetHelper.addLogEntry(meet_id, f"User {user_email} joined the meeting")
        
        return jsonify({
            "success": True,
            "redirectUrl": f"https://192.168.100.183:7053/room/{meet_id}/{user_email}"
        }), 200
        
    except Exception as e:
        logger.error(f"Error joining meeting: {str(e)}")
        return jsonify({"error": "Failed to join meeting"}), 500

@app.route("/room/<meet_id>/<user_email>")
def room(meet_id, user_email):
    """
    Render the meeting room page
    """
    userMail = user_email
    meet = MeetHelper.getMeetingByID(meet_id)
    
    if not meet:
        return "Meeting not found", 404

    participants = meet.getInvitedEmployeesList()

    if userMail not in participants:
        return "You are not a member of this meet", 403

    return render_template("video.html", meet_id=meet_id, user_mail=userMail, server="https://192.168.0.94:7050") #hadi badelha dynamic


# =================== NEW MEETING API ENDPOINTS ===================

@app.route("/meetings", methods=["GET"])
def get_all_meetings():
    """
    Get all meetings with optional filters
    Query params: user_email, is_active
    """
    try:
        user_email = request.args.get('user_email')
        is_active = request.args.get('is_active')
        
        # Convert is_active to boolean if provided
        is_active_bool = None
        if is_active:
            is_active_bool = is_active.lower() == 'true'
        
        meetings = MeetHelper.getAllMeetings(user_email, is_active_bool)
        
        # Format response
        meetings_data = [{
            "id": m.getDatabaseID(),
            "meeting_id": m.getID(),
            "title": m.getTitle(),
            "invitation_link": m.getInvitationLink(),
            "created_by": m.getCreatedBy(),
            "created_at": m.getCreatedAt(),
            "is_active": m.getIsActive(),
            "has_password": bool(m.getPassword())
        } for m in meetings]
        
        return jsonify({"data": meetings_data}), 200
        
    except Exception as e:
        logger.error(f"Error getting meetings: {str(e)}")
        return jsonify({"error": "Failed to get meetings"}), 500


@app.route("/meetings/<meeting_id>", methods=["GET"])
def get_meeting(meeting_id):
    """
    Get specific meeting by ID
    """
    try:
        meeting = MeetHelper.getMeetingByID(meeting_id)
        
        if not meeting:
            return jsonify({"error": "Meeting not found"}), 404
        
        return jsonify({
            "id": meeting.getDatabaseID(),
            "meeting_id": meeting.getID(),
            "title": meeting.getTitle(),
            "object": meeting.getObject(),
            "description": meeting.getDescription(),
            "log_path": meeting.getLogPath(),
            "invited_employees_list": meeting.getInvitedEmployeesList(),
            "created_by": meeting.getCreatedBy(),
            "created_at": meeting.getCreatedAt(),
            "is_active": meeting.getIsActive(),
            "started_at": meeting.getStartedAt(),
            "ended_at": meeting.getEndedAt()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting meeting: {str(e)}")
        return jsonify({"error": "Failed to get meeting"}), 500


@app.route("/meetings/<meeting_id>", methods=["PUT"])
def update_meeting(meeting_id):
    """
    Update meeting details
    """
    try:
        updates = request.json
        
        if not updates:
            return jsonify({"error": "No updates provided"}), 400
        
        success = MeetHelper.updateMeeting(meeting_id, updates)
        
        if success:
            return jsonify({
                "success": True,
                "meeting_id": meeting_id,
                "message": "Meeting updated successfully"
            }), 200
        else:
            return jsonify({"error": "Failed to update meeting"}), 500
            
    except Exception as e:
        logger.error(f"Error updating meeting: {str(e)}")
        return jsonify({"error": "Failed to update meeting"}), 500


@app.route("/meetings/<meeting_id>", methods=["DELETE"])
def delete_meeting(meeting_id):
    """
    Delete (soft delete) a meeting
    """
    try:
        success = MeetHelper.deleteMeeting(meeting_id)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Meeting deleted successfully"
            }), 200
        else:
            return jsonify({"error": "Failed to delete meeting"}), 500
            
    except Exception as e:
        logger.error(f"Error deleting meeting: {str(e)}")
        return jsonify({"error": "Failed to delete meeting"}), 500


@app.route("/meetings/<meeting_id>/start", methods=["POST"])
def start_meeting(meeting_id):
    """
    Mark meeting as started and log the event
    """
    try:
        success = MeetHelper.startMeeting(meeting_id)
        
        if success:
            MeetHelper.addLogEntry(meeting_id, "Meeting started")
            return jsonify({
                "success": True,
                "meeting_id": meeting_id,
                "message": "Meeting started"
            }), 200
        else:
            return jsonify({"error": "Failed to start meeting"}), 500
            
    except Exception as e:
        logger.error(f"Error starting meeting: {str(e)}")
        return jsonify({"error": "Failed to start meeting"}), 500


@app.route("/meetings/<meeting_id>/end", methods=["POST"])
def end_meeting(meeting_id):
    """
    Mark meeting as ended and log the event
    """
    try:
        success = MeetHelper.endMeeting(meeting_id)
        
        if success:
            MeetHelper.addLogEntry(meeting_id, "Meeting ended")
            return jsonify({
                "success": True,
                "meeting_id": meeting_id,
                "message": "Meeting ended"
            }), 200
        else:
            return jsonify({"error": "Failed to end meeting"}), 500
            
    except Exception as e:
        logger.error(f"Error ending meeting: {str(e)}")
        return jsonify({"error": "Failed to end meeting"}), 500


@app.route("/meetings/<meeting_id>/log", methods=["POST"])
def add_meeting_log(meeting_id):
    """
    Add a log entry to the meeting log
    """
    try:
        data = request.json
        log_entry = data.get("log_entry")
        
        if not log_entry:
            return jsonify({"error": "log_entry is required"}), 400
        
        success = MeetHelper.addLogEntry(meeting_id, log_entry)
        
        if success:
            return jsonify({
                "success": True,
                "message": "Log entry added"
            }), 200
        else:
            return jsonify({"error": "Failed to add log entry"}), 500
            
    except Exception as e:
        logger.error(f"Error adding log entry: {str(e)}")
        return jsonify({"error": "Failed to add log entry"}), 500


@app.route("/meetings/<meeting_id>/log", methods=["GET"])
def get_meeting_log(meeting_id):
    """
    Get meeting log content
    """
    try:
        log_content = MeetHelper.getMeetingLog(meeting_id)
        
        if log_content is not None:
            return jsonify({
                "meeting_id": meeting_id,
                "log_content": log_content
            }), 200
        else:
            return jsonify({"error": "Failed to get log"}), 500
            
    except Exception as e:
        logger.error(f"Error getting log: {str(e)}")
        return jsonify({"error": "Failed to get log"}), 500


# =================== SOCKETIO EVENTS ===================

@socketio.on('connect')
def handle_connect():
    user_email = request.args.get("user_email")
    logger.info(f'Client connected: {request.sid} user_email: {user_email}')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f'Client disconnected: {request.sid}')

    # Find and remove user from any rooms they were in
    for room_id in list(rooms.keys()):
        if request.sid in rooms[room_id]:
            rooms[room_id].pop(request.sid)
            emit('peer-disconnected', {'peerId': request.sid}, room=room_id, skip_sid=request.sid)
            
            if len(rooms[room_id]) == 0:
                del rooms[room_id]

@socketio.on('join')
def handle_join(data):
    room_id = data['room']
    user_id = request.sid
    user_email = data.get('user_email')

    logger.info(f'User {user_id} (email: {user_email}) joining room: {room_id}')

    # Create room if it doesn't exist
    if room_id not in rooms:
        rooms[room_id] = {}

    # Add user to room
    join_room(room_id)
    rooms[room_id][user_id] = {'user_email': user_email, 'joined': True}

    # Get peer info with emails (excluding current user)
    peer_info = [{'id': peer_id, 'user_email': peer_data.get('user_email')} 
                 for peer_id, peer_data in rooms[room_id].items() if peer_id != user_id]

    # Get list of peer IDs (excluding current user)
    peer_ids = [peer_id for peer_id in rooms[room_id].keys() if peer_id != user_id]

    # Confirm room joined
    emit('room-joined', {
        'room': room_id,
        'peers': peer_ids,
        'peerInfo': peer_info
    })

    # Notify others that a new peer joined
    emit('new-peer', {
        'peerId': user_id,
        'user_email': user_email
    }, room=room_id, skip_sid=user_id)
    
    # Log the join event
    if user_email:
        MeetHelper.addLogEntry(room_id, f"User {user_email} joined the room")

@socketio.on('leave')
def handle_leave(data):
    room_id = data['room']
    user_id = request.sid

    logger.info(f'User {user_id} leaving room: {room_id}')

    # Remove user from room
    if room_id in rooms and user_id in rooms[room_id]:
        user_email = rooms[room_id][user_id].get('user_email')
        
        leave_room(room_id)
        del rooms[room_id][user_id]

        # Notify others that peer left
        emit('peer-disconnected', {'peerId': user_id}, room=room_id)

        # Log the leave event
        if user_email:
            MeetHelper.addLogEntry(room_id, f"User {user_email} left the room")

        # Delete room if empty
        if len(rooms[room_id]) == 0:
            del rooms[room_id]

@socketio.on('offer')
def handle_offer(data):
    room_id = data['room']
    target_id = data['targetId']
    offer = data['offer']
    user_email = data.get('user_email')

    logger.info(f'Relaying offer from {request.sid} (email: {user_email}) to {target_id}')

    # Send the offer to the target peer
    emit('offer', {
        'peerId': request.sid,
        'offer': offer,
        'user_email': user_email
    }, room=target_id)

@socketio.on('answer')
def handle_answer(data):
    room_id = data['room']
    target_id = data['targetId']
    answer = data['answer']
    user_email = data.get('user_email')

    logger.info(f'Relaying answer from {request.sid} (email: {user_email}) to {target_id}')

    # Send the answer to the target peer
    emit('answer', {
        'peerId': request.sid,
        'answer': answer,
        'user_email': user_email
    }, room=target_id)

@socketio.on('ice-candidate')
def handle_ice_candidate(data):
    room_id = data['room']
    target_id = data['targetId']
    candidate = data['candidate']

    # Send the ICE candidate to the target peer
    emit('ice-candidate', {
        'peerId': request.sid,
        'candidate': candidate
    }, room=target_id)

if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=7053,
        certfile='meetingService\\certifs\\cert.pem',
        keyfile='meetingService\\certifs\\key.pem',
        debug=True, allow_unsafe_werkzeug=True
     )
