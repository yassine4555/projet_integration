import dotenv from 'dotenv';
import express from 'express';
import http from 'http';
import { Server } from 'socket.io';
import { createClient } from 'redis';

dotenv.config();

const app = express();
const server = http.createServer(app);
const io = new Server(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
  }
});

// Initialize Redis clients
const pubClient = createClient();
const subClient = createClient();
await pubClient.connect();
await subClient.connect();

// Store all active games: { matchCode: gameData }
const games = new Map();

// Generate a random 6-character match code
function generateMatchCode() {
  return Math.random().toString(36).substring(2, 8).toUpperCase();
}

// Initialize a new game
function createGame(matchCode) {
  return {
    board: Array(9).fill(null),
    xIsNext: true,
    players: { X: null, O: null }, // socket IDs
    spectators: [],
    winner: null,
  };
}

// Subscribe to Redis for cross-server game updates
await subClient.subscribe('game-updates', (message) => {
  const { matchCode, gameState } = JSON.parse(message);
  games.set(matchCode, gameState);
  io.to(matchCode).emit('gameState', gameState);
});

io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  // Create a new match
  socket.on('createMatch', () => {
    const matchCode = generateMatchCode();
    const game = createGame(matchCode);
    game.players.X = socket.id;
    games.set(matchCode, game);
    
    socket.join(matchCode);
    socket.emit('matchCreated', { matchCode, role: 'X' });
    socket.emit('gameState', game);
  });

  // Join an existing match
  socket.on('joinMatch', (matchCode) => {
    const game = games.get(matchCode);
    
    if (!game) {
      socket.emit('error', 'Match not found');
      return;
    }

    socket.join(matchCode);
    let role = 'spectator';

    // Assign player roles
    if (!game.players.X) {
      game.players.X = socket.id;
      role = 'X';
    } else if (!game.players.O) {
      game.players.O = socket.id;
      role = 'O';
    } else {
      game.spectators.push(socket.id);
    }

    socket.emit('matchJoined', { matchCode, role });
    io.to(matchCode).emit('gameState', game);
  });

  // Handle player moves
  socket.on('makeMove', ({ matchCode, index }) => {
    const game = games.get(matchCode);
    if (!game) return;

    // Check if it's this player's turn
    const currentPlayer = game.xIsNext ? 'X' : 'O';
    if (game.players[currentPlayer] !== socket.id) return;

    // Check if move is valid
    if (game.board[index] || game.winner) return;

    // Make the move
    game.board[index] = currentPlayer;
    game.xIsNext = !game.xIsNext;
    game.winner = calculateWinner(game.board);

    // Publish to Redis and emit to all clients in the room
    pubClient.publish('game-updates', JSON.stringify({ matchCode, gameState: game }));
    io.to(matchCode).emit('gameState', game);
  });

  // Restart game
  socket.on('restartGame', (matchCode) => {
    const game = games.get(matchCode);
    if (!game) return;

    // Only players can restart
    if (game.players.X !== socket.id && game.players.O !== socket.id) return;

    game.board = Array(9).fill(null);
    game.xIsNext = true;
    game.winner = null;

    io.to(matchCode).emit('gameState', game);
  });

  socket.on('disconnect', () => {
    console.log('Client disconnected:', socket.id);
    
    // Remove player from all games
    for (const [matchCode, game] of games.entries()) {
      if (game.players.X === socket.id) game.players.X = null;
      if (game.players.O === socket.id) game.players.O = null;
      game.spectators = game.spectators.filter(id => id !== socket.id);
      
      io.to(matchCode).emit('gameState', game);
    }
  });
});

function calculateWinner(board) {
  const lines = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [0, 3, 6], [1, 4, 7], [2, 5, 8],
    [0, 4, 8], [2, 4, 6]
  ];
  for (let [a, b, c] of lines) {
    if (board[a] && board[a] === board[b] && board[a] === board[c]) {
      return board[a];
    }
  }
  return null;
}

const PORT = process.env.PORT || 7054;
server.listen(PORT, () => {
  console.log(`✅ Server running on http://192.168.100.190:${PORT}`);
});