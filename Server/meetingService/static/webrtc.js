// Global variables
let localStream = null;
let peerConnections = {}; // Store multiple peer connections
let socket = null;
let roomId = null;
let participantCount = 0;
let isJoining = false; // Prevent multiple join attempts
let reconnectAttempts = 0;
let maxReconnectAttempts = 3;
let reconnectInterval = 2000; // 2 seconds
let peerUserEmails = {}; // Store peer emails

// DOM elements
const startButton = document.getElementById('startButton');
const callButton = document.getElementById('callButton');
const hangupButton = document.getElementById('hangupButton');
const toggleAudioButton = document.getElementById('toggleAudioButton');
const toggleVideoButton = document.getElementById('toggleVideoButton');
const localVideo = document.getElementById('localVideo');
const videoGrid = document.getElementById('videoGrid');
const statusDiv = document.getElementById('status');
const participantCountElement = document.getElementById('participantCount');

const configuration = {
    iceServers: [
        { urls: 'stun:stun.l.google.com:19302' },
        { urls: 'stun:stun1.l.google.com:19302' },

        // Add free TURN servers for better NAT traversal
        {
            urls: 'turn:openrelay.metered.ca:80',
            username: 'openrelayproject',
            credential: 'openrelayproject'
        },
        {
            urls: 'turn:openrelay.metered.ca:443',
            username: 'openrelayproject',
            credential: 'openrelayproject'
        }
    ],
    iceCandidatePoolSize: 10 // Increase pool size for better connectivity
};

// Connect to Socket.IO server with reconnection logic
function connectSocket() {
    console.log('User email:', user_mail);
    if (socket && socket.connected) {
        console.log("Socket already connected");
        return;
    }

    updateStatus('Connecting to signaling server...');
    
    // Use your server URL here (HTTP or HTTPS)
    socket = io.connect(SERVER, {
        secure: true,
        rejectUnauthorized: false,  // Accept self-signed certificates
        reconnection: true,
        reconnectionAttempts: 5,
        reconnectionDelay: 1000,
        timeout: 10000,
        query: {
            user_email: user_mail
        }
    });

    // Socket event handlers
    socket.on('connect', () => {
        updateStatus('Connected to signaling server');
        reconnectAttempts = 0; // Reset reconnect attempts on successful connection

        // If we were in a room before reconnection, rejoin it
        if (roomId && localStream) {
            setTimeout(() => {
                joinRoom(roomId, true); // rejoin flag
            }, 1000);
        }
    });

    socket.on('connect_error', (error) => {
        console.error('Connection error:', error);
        updateStatus('Connection error. Retrying...');
        handleSocketReconnect();
    });

    socket.on('disconnect', () => {
        updateStatus('Disconnected from signaling server');
        handleSocketReconnect();
    });

    // Handle room joined event
    socket.on('room-joined', (data) => {
        updateStatus(`Joined room: ${data.room}`);
        roomId = data.room;
        isJoining = false;

        // Store peer emails if provided
        if (data.peerInfo && data.peerInfo.length > 0) {
            data.peerInfo.forEach(peer => {
                peerUserEmails[peer.id] = peer.user_email;
            });
        }

        updateParticipantCount(data.peers.length);

        // Enable/disable buttons
        callButton.disabled = true;
        hangupButton.disabled = false;

        // Create peer connections with existing participants
        if (data.peers && data.peers.length > 0) {
            data.peers.forEach(peerId => {
                if (peerId !== socket.id) {
                    setTimeout(() => {
                        createPeerConnection(peerId);
                        sendOffer(peerId);
                    }, 500); // Small delay between each connection setup
                }
            });
        }
    });

    // Handle new peer joined
    socket.on('new-peer', (data) => {
        const peerId = data.peerId;

        // Store user email if provided
        if (data.user_email) {
            peerUserEmails[peerId] = data.user_email;
        }

        updateStatus(`New peer joined: ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`);

        // Small delay to ensure both sides aren't creating connections simultaneously
        setTimeout(() => {
            // Create a new peer connection for this peer
            createPeerConnection(peerId);
            // The new peer will send us an offer
        }, 1000);

        // Update participant count
        updateParticipantCount(participantCount + 1);
    });

    // Handle peer disconnected
    socket.on('peer-disconnected', (data) => {
        const peerId = data.peerId;
        const peerEmail = peerUserEmails[peerId] || peerId.substring(0, 5);
        updateStatus(`Peer disconnected: ${peerEmail}...`);

        // Remove peer connection and video
        removePeerConnection(peerId);

        // Remove from email mapping
        delete peerUserEmails[peerId];

        // Update participant count
        updateParticipantCount(participantCount - 1);
    });

    // Handle offers from other peers
    socket.on('offer', async (data) => {
        const peerId = data.peerId;
        const offer = data.offer;

        // Store user email if provided
        if (data.user_email) {
            peerUserEmails[peerId] = data.user_email;
        }

        console.log(`Received offer from: ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`, offer);
        updateStatus(`Received offer from: ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`);

        // Create peer connection if it doesn't exist
        if (!peerConnections[peerId]) {
            createPeerConnection(peerId);
        }

        try {
            await handleOffer(peerId, offer);
        } catch (error) {
            console.error("Error handling offer:", error);
            // Try to recover by recreating the connection
            recreatePeerConnection(peerId);
        }
    });

    // Handle answers from other peers
    socket.on('answer', async (data) => {
        const peerId = data.peerId;
        const answer = data.answer;

        // Store user email if provided
        if (data.user_email) {
            peerUserEmails[peerId] = data.user_email;
        }

        console.log(`Received answer from: ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`, answer);
        updateStatus(`Received answer from: ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`);

        try {
            await handleAnswer(peerId, answer);
        } catch (error) {
            console.error("Error handling answer:", error);
            // Try to recover by recreating the connection
            recreatePeerConnection(peerId);
        }
    });

    // Handle ICE candidates from other peers
    socket.on('ice-candidate', async (data) => {
        const peerId = data.peerId;
        const candidate = data.candidate;

        try {
            await handleNewICECandidate(peerId, candidate);
        } catch (error) {
            console.error("Error handling ICE candidate:", error);
        }
    });

    // Handle room full error
    socket.on('room-full', (data) => {
        updateStatus(`Room ${data.room} is full`);
        isJoining = false;
    });
}

// Handle socket reconnection
function handleSocketReconnect() {
    if (reconnectAttempts >= maxReconnectAttempts) {
        updateStatus("Could not reconnect to the server. Please refresh the page.");
        return;
    }

    reconnectAttempts++;
    updateStatus(`Reconnecting... Attempt ${reconnectAttempts}/${maxReconnectAttempts}`);

    setTimeout(() => {
        if (!socket || !socket.connected) {
            connectSocket();
        }
    }, reconnectInterval);
}

// Recreate peer connection if there's an error
function recreatePeerConnection(peerId) {
    console.log(`Recreating peer connection for ${peerId}`);

    // Remove existing connection
    if (peerConnections[peerId]) {
        const peerConnection = peerConnections[peerId].connection;
        if (peerConnection) {
            peerConnection.close();
        }
        delete peerConnections[peerId];
    }

    // Create new connection
    setTimeout(() => {
        createPeerConnection(peerId);
        sendOffer(peerId);
    }, 1000);
}

// Initialize the application
function init() {
    connectSocket();

    // Add event listeners to buttons
    startButton.addEventListener('click', startStream);
    callButton.addEventListener('click', () => joinRoom());
    hangupButton.addEventListener('click', hangUp);
    toggleAudioButton.addEventListener('click', toggleAudio);
    toggleVideoButton.addEventListener('click', toggleVideo);

    updateStatus('App initialized. Click "Start" to begin.');

    // Set up local video label with current user's email
    const localVideoContainer = document.getElementById('localVideoContainer');
    if (localVideoContainer) {
        const localNameLabel = document.createElement('div');
        localNameLabel.className = 'peer-name';
        localNameLabel.textContent = `${user_mail} (You)`;
        localVideoContainer.appendChild(localNameLabel);
    }
}

// Start local video stream
async function startStream() {
    try {
        // Request access to webcam and microphone
        localStream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: 640 },
                height: { ideal: 480 },
                frameRate: { ideal: 30 }
            },
            audio: {
                echoCancellation: true,
                noiseSuppression: true
            }
        });

        // Display local video stream
        localVideo.srcObject = localStream;

        // Enable buttons
        startButton.disabled = true;
        callButton.disabled = false;
        toggleAudioButton.disabled = false;
        toggleVideoButton.disabled = false;

        updateStatus('Local stream started');
    } catch (error) {
        updateStatus(`Error starting stream: ${error.message}`);
        console.error('Error starting stream:', error);
    }
}

// Join a meeting room
function joinRoom(roomIdParam, isRejoin = false) {
    // Prevent multiple join attempts
    if (isJoining && !isRejoin) {
        updateStatus('Already attempting to join. Please wait...');
        return;
    }

    isJoining = true;

    // Use provided room ID or get from input
    let targetRoomId = roomIdParam || RoomId;

    if (!targetRoomId) {
        updateStatus('Please enter a room ID');
        isJoining = false;
        return;
    }

    if (!localStream) {
        updateStatus('Please start your video first');
        isJoining = false;
        return;
    }

    updateStatus(`${isRejoin ? 'Rejoining' : 'Joining'} room: ${targetRoomId}`);

    // Clear any existing peer connections if rejoining
    if (isRejoin) {
        Object.keys(peerConnections).forEach(peerId => {
            removePeerConnection(peerId);
        });
    }

    // Join the specified room with user email
    socket.emit('join', {
        room: targetRoomId,
        user_email: user_mail
    });

    // Set a timeout for join operation
    setTimeout(() => {
        if (isJoining) {
            isJoining = false;
            updateStatus(`Join operation timed out. Please try again.`);
        }
    }, 10000); // 10 second timeout
}

// Create WebRTC peer connection with improved error handling
function createPeerConnection(peerId) {
    console.log(`Creating peer connection for ${peerId}`);

    // If connection already exists, close it first
    if (peerConnections[peerId] && peerConnections[peerId].connection) {
        console.log(`Closing existing connection for ${peerId}`);
        try {
            peerConnections[peerId].connection.close();
        } catch (e) {
            console.error("Error closing connection:", e);
        }
    }

    try {
        const peerConnection = new RTCPeerConnection(configuration);

        // Add local stream tracks to peer connection
        if (localStream) {
            localStream.getTracks().forEach(track => {
                peerConnection.addTrack(track, localStream);
            });
        }

        // Set up event handlers for peer connection
        peerConnection.onicecandidate = (event) => handleICECandidate(peerId, event);
        peerConnection.ontrack = (event) => handleTrackEvent(peerId, event);
        peerConnection.oniceconnectionstatechange = () => handleICEConnectionStateChange(peerId);

        // Store the peer connection
        peerConnections[peerId] = {
            connection: peerConnection,
            iceCandidatesBuffer: [],
            pendingOffer: null,
            pendingAnswer: null,
            connectionState: 'new'
        };

        // Add event listener for connection state changes
        peerConnection.onconnectionstatechange = () => {
            console.log(`Connection state changed for ${peerId}: ${peerConnection.connectionState}`);
            peerConnections[peerId].connectionState = peerConnection.connectionState;

            if (peerConnection.connectionState === 'connected') {
                updateStatus(`Connected to peer ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`);
            } else if (peerConnection.connectionState === 'failed') {
                updateStatus(`Connection to peer ${peerUserEmails[peerId] || peerId.substring(0, 5)}... failed`);
                // Try to reconnect
                setTimeout(() => {
                    recreatePeerConnection(peerId);
                }, 2000);
            }
        };

        updateStatus(`Peer connection created for ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`);
        return peerConnection;
    } catch (error) {
        console.error(`Error creating peer connection: ${error}`);
        updateStatus(`Error creating connection: ${error.message}`);
        return null;
    }
}

// Create and send an offer to a specific peer
async function sendOffer(peerId) {
    const peerData = peerConnections[peerId];
    if (!peerData || !peerData.connection) return;

    const peerConnection = peerData.connection;

    try {
        // Create an offer with specific constraints for better performance
        const offer = await peerConnection.createOffer({
            offerToReceiveAudio: true,
            offerToReceiveVideo: true,
            iceRestart: peerData.connectionState === 'failed' // Use ice restart if connection failed
        });

        await peerConnection.setLocalDescription(offer);

        // Wait a bit to gather ICE candidates
        await new Promise(resolve => setTimeout(resolve, 1000));

        socket.emit('offer', {
            room: roomId,
            targetId: peerId,
            offer: peerConnection.localDescription,
            user_email: user_mail
        });

        console.log(`Sent offer to ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`, peerConnection.localDescription);
        updateStatus(`Sent offer to ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`);
    } catch (error) {
        updateStatus(`Error creating offer: ${error.message}`);
        console.error('Error creating offer:', error);
    }
}

// Handle incoming offer from a peer with perfect negotiation pattern
async function handleOffer(peerId, offer) {
    const peerData = peerConnections[peerId];
    if (!peerData || !peerData.connection) return;

    const peerConnection = peerData.connection;

    try {
        const offerCollision = peerConnection.signalingState !== 'stable';

        // Determine which peer is "polite" based on socket IDs
        const isPolitePeer = socket.id > peerId;

        console.log(`Handling offer collision: ${offerCollision}, isPolitePeer: ${isPolitePeer}`);

        // If we have a collision and we're the impolite peer, ignore this offer
        if (offerCollision && !isPolitePeer) {
            console.log('Ignoring offer due to collision (impolite peer)');
            return;
        }

        // If we're the polite peer or no collision, proceed
        if (offerCollision) {
            console.log('Rolling back local description due to collision (polite peer)');
            await Promise.all([
                peerConnection.setLocalDescription({type: 'rollback'}),
                peerConnection.setRemoteDescription(new RTCSessionDescription(offer))
            ]);
        } else {
            await peerConnection.setRemoteDescription(new RTCSessionDescription(offer));
        }

        // Process any buffered ICE candidates
        await processBufferedIceCandidates(peerId);

        // Create and send an answer
        const answer = await peerConnection.createAnswer();
        await peerConnection.setLocalDescription(answer);

        // Wait a bit to gather ICE candidates
        await new Promise(resolve => setTimeout(resolve, 1000));

        socket.emit('answer', {
            room: roomId,
            targetId: peerId,
            answer: peerConnection.localDescription,
            user_email: user_mail
        });

        console.log(`Sent answer to ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`, peerConnection.localDescription);
        updateStatus(`Sent answer to ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`);

    } catch (error) {
        updateStatus(`Error handling offer: ${error.message}`);
        console.error('Error handling offer:', error);
        throw error; // Rethrow for higher level handling
    }
}

// Handle incoming answer from a peer
async function handleAnswer(peerId, answer) {
    const peerData = peerConnections[peerId];
    if (!peerData || !peerData.connection) return;

    const peerConnection = peerData.connection;

    try {
        const validStates = ['have-local-offer', 'stable'];
        if (validStates.includes(peerConnection.signalingState)) {
            await peerConnection.setRemoteDescription(new RTCSessionDescription(answer));

            // Process any buffered ICE candidates
            await processBufferedIceCandidates(peerId);

            updateStatus(`Connection established with ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`);
        } else {
            console.warn(`Cannot process answer: connection in state ${peerConnection.signalingState}`);

            // Store answer for later
            peerData.pendingAnswer = answer;

            // Try to reset the connection
            setTimeout(() => {
                if (peerData.pendingAnswer) {
                    console.log("Attempting to apply saved answer");
                    peerConnection.setRemoteDescription(new RTCSessionDescription(peerData.pendingAnswer))
                        .then(() => {
                            peerData.pendingAnswer = null;
                            processBufferedIceCandidates(peerId);
                        })
                        .catch(err => {
                            console.error("Error applying saved answer:", err);
                        });
                }
            }, 2000);
        }
    } catch (error) {
        updateStatus(`Error handling answer: ${error.message}`);
        console.error('Error handling answer:', error);
        throw error; // Rethrow for higher level handling
    }
}

// Process buffered ICE candidates for a specific peer
async function processBufferedIceCandidates(peerId) {
    const peerData = peerConnections[peerId];
    if (!peerData || !peerData.connection || !peerData.iceCandidatesBuffer.length) return;

    const peerConnection = peerData.connection;
    const iceCandidatesBuffer = peerData.iceCandidatesBuffer;

    console.log(`Processing ${iceCandidatesBuffer.length} buffered ICE candidates for ${peerId}`);

    try {
        // Check if we have a remote description
        if (peerConnection.remoteDescription && peerConnection.remoteDescription.type) {
            // Process all buffered candidates
            for (const candidate of iceCandidatesBuffer) {
                try {
                    await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
                } catch (e) {
                    console.warn(`Failed to add ICE candidate: ${e.message}`);
                }
            }
            // Clear the buffer
            peerData.iceCandidatesBuffer = [];
        }
    } catch (error) {
        console.error('Error processing buffered ICE candidates:', error);
    }
}

// Handle ICE candidates
function handleICECandidate(peerId, event) {
    if (event.candidate) {
        socket.emit('ice-candidate', {
            room: roomId,
            targetId: peerId,
            candidate: event.candidate
        });
    }
}

// Handle new ICE candidate from a peer
async function handleNewICECandidate(peerId, candidate) {
    const peerData = peerConnections[peerId];
    if (!peerData || !peerData.connection) return;

    const peerConnection = peerData.connection;

    try {
        if (peerConnection.remoteDescription && peerConnection.remoteDescription.type) {
            await peerConnection.addIceCandidate(new RTCIceCandidate(candidate));
        } else {
            // If no remote description, buffer the candidate
            peerData.iceCandidatesBuffer.push(candidate);
            console.log(`Buffered ICE candidate for ${peerId}, total: ${peerData.iceCandidatesBuffer.length}`);
        }
    } catch (error) {
        console.error('Error adding ICE candidate:', error);
    }
}

// Handle incoming tracks from a peer
function handleTrackEvent(peerId, event) {
    console.log(`Received track from ${peerId}:`, event);

    if (event.streams && event.streams[0]) {
        // Create or update video element
        createOrUpdateVideoElement(peerId, event.streams[0]);
        updateStatus(`Receiving stream from ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`);
    }
}

// Handle ICE connection state changes
function handleICEConnectionStateChange(peerId) {
    const peerData = peerConnections[peerId];
    if (!peerData || !peerData.connection) return;

    const peerConnection = peerData.connection;
    console.log(`ICE connection state change for ${peerId}: ${peerConnection.iceConnectionState}`);

    switch (peerConnection.iceConnectionState) {
        case 'connected':
            updateStatus(`ICE Connected to ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`);
            break;

        case 'disconnected':
            updateStatus(`ICE Disconnected from ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`);
            // Wait a bit to see if it reconnects automatically
            setTimeout(() => {
                if (peerConnections[peerId] &&
                    peerConnections[peerId].connection.iceConnectionState === 'disconnected') {
                    recreatePeerConnection(peerId);
                }
            }, 5000);
            break;

        case 'failed':
            updateStatus(`ICE Connection failed with ${peerUserEmails[peerId] || peerId.substring(0, 5)}...`);
            // Recreate the connection
            recreatePeerConnection(peerId);
            break;

        case 'closed':
            removePeerConnection(peerId);
            break;
    }
}

// Create or update video element for a peer
function createOrUpdateVideoElement(peerId, stream) {
    // Check if video element already exists
    let videoElement = document.getElementById(`video-${peerId}`);

    if (!videoElement) {
        // Create new video container
        const videoContainer = document.createElement('div');
        videoContainer.id = `container-${peerId}`;
        videoContainer.className = 'video-item';

        // Create video element
        videoElement = document.createElement('video');
        videoElement.id = `video-${peerId}`;
        videoElement.autoplay = true;
        videoElement.playsInline = true;

        // Create peer name label
        const peerName = document.createElement('div');
        peerName.className = 'peer-name';

        // Use email if available, otherwise fallback to peer ID
        peerName.textContent = peerUserEmails[peerId] || `Peer ${peerId.substring(0, 5)}...`;

        // Add elements to container
        videoContainer.appendChild(videoElement);
        videoContainer.appendChild(peerName);

        // Add container to grid
        videoGrid.appendChild(videoContainer);
    }

    // Set stream as source
    if (videoElement.srcObject !== stream) {
        videoElement.srcObject = stream;
    }

    // Ensure video plays automatically
    videoElement.play().catch(e => console.log('Error auto-playing video:', e));
}

// Remove a peer connection and its video element
function removePeerConnection(peerId) {
    // Close and remove the peer connection
    if (peerConnections[peerId]) {
        const peerConnection = peerConnections[peerId].connection;
        if (peerConnection) {
            try {
                peerConnection.close();
            } catch (e) {
                console.error("Error closing connection:", e);
            }
        }
        delete peerConnections[peerId];
    }

    // Remove the video container
    const videoContainer = document.getElementById(`container-${peerId}`);
    if (videoContainer) {
        videoGrid.removeChild(videoContainer);
    }
}

// Toggle audio on/off
function toggleAudio() {
    if (!localStream) return;

    const audioTracks = localStream.getAudioTracks();
    if (audioTracks.length === 0) return;

    const enabled = !audioTracks[0].enabled;
    audioTracks.forEach(track => {
        track.enabled = enabled;
    });

    toggleAudioButton.textContent = enabled ? '🎤' : '🔇';
    updateStatus(`Microphone ${enabled ? 'unmuted' : 'muted'}`);
}

// Toggle video on/off
function toggleVideo() {
    if (!localStream) return;

    const videoTracks = localStream.getVideoTracks();
    if (videoTracks.length === 0) return;

    const enabled = !videoTracks[0].enabled;
    videoTracks.forEach(track => {
        track.enabled = enabled;
    });

    toggleVideoButton.textContent = enabled ? '👁️' : '🚫';
    updateStatus(`Camera ${enabled ? 'turned on' : 'turned off'}`);
}

// Hang up the call and leave the room
function hangUp() {
    if (socket && roomId) {
        socket.emit('leave', { room: roomId });
    }

    // Close all peer connections
    Object.keys(peerConnections).forEach(peerId => {
        removePeerConnection(peerId);
    });

    // Reset UI
    videoGrid.innerHTML = '';
    callButton.disabled = !localStream;
    hangupButton.disabled = true;
    updateParticipantCount(0);

    // Reset room ID and clear emails
    roomId = null;
    peerUserEmails = {};

    updateStatus('Left the meeting');
}

// Update participant count
function updateParticipantCount(count) {
    participantCount = count;
    participantCountElement.textContent = `Participants: ${count + 1}`; // +1 for self
}

// Update status message
function updateStatus(message) {
    statusDiv.textContent = message;
    console.log(message);
}

// Initialize the app when the page loads
window.addEventListener('load', init);