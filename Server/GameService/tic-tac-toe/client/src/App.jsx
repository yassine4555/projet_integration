import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';

const socket = io('https://192.168.100.190:7050/game');

function App() {
  const [gameState, setGameState] = useState(null);
  const [matchCode, setMatchCode] = useState('');
  const [inputCode, setInputCode] = useState('');
  const [role, setRole] = useState(null);
  const [inGame, setInGame] = useState(false);

  useEffect(() => {
    socket.on('matchCreated', ({ matchCode, role }) => {
      setMatchCode(matchCode);
      setRole(role);
      setInGame(true);
    });

    socket.on('matchJoined', ({ matchCode, role }) => {
      setMatchCode(matchCode);
      setRole(role);
      setInGame(true);
    });

    socket.on('gameState', (state) => {
      setGameState(state);
    });

    socket.on('error', (message) => {
      alert(message);
    });

    return () => {
      socket.off('matchCreated');
      socket.off('matchJoined');
      socket.off('gameState');
      socket.off('error');
    };
  }, []);

  const createMatch = () => {
    socket.emit('createMatch');
  };

  const joinMatch = () => {
    if (inputCode.trim()) {
      socket.emit('joinMatch', inputCode.trim().toUpperCase());
    }
  };

  const handleClick = (index) => {
    if (!gameState || role === 'spectator') return;
    if (gameState.board[index] || gameState.winner) return;
    
    const currentPlayer = gameState.xIsNext ? 'X' : 'O';
    if (role !== currentPlayer) return;

    socket.emit('makeMove', { matchCode, index });
  };

  const restartGame = () => {
    socket.emit('restartGame', matchCode);
  };

  const calculateWinner = (board) => {
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
  };

  // Lobby screen
  if (!inGame) {
    return (
      <div style={{ textAlign: 'center', marginTop: '50px' }}>
        <h1>Multiplayer Tic-Tac-Toe</h1>
        
        <div style={{ marginTop: '30px' }}>
          <button onClick={createMatch} style={{ fontSize: '18px', padding: '10px 20px' }}>
            Create New Match
          </button>
        </div>

        <div style={{ marginTop: '30px' }}>
          <h3>Or Join a Match</h3>
          <input
            type="text"
            placeholder="Enter match code"
            value={inputCode}
            onChange={(e) => setInputCode(e.target.value)}
            style={{ padding: '10px', fontSize: '16px', marginRight: '10px' }}
          />
          <button onClick={joinMatch} style={{ fontSize: '16px', padding: '10px 20px' }}>
            Join Match
          </button>
        </div>
      </div>
    );
  }

  // Game screen
  if (!gameState) return <div>Loading...</div>;

  const winner = gameState.winner;
  const isDraw = !winner && gameState.board.every(cell => cell !== null);
  
  let status;
  if (winner) {
    status = `Winner: ${winner}`;
  } else if (isDraw) {
    status = 'Draw!';
  } else {
    status = `Next player: ${gameState.xIsNext ? 'X' : 'O'}`;
  }

  const isMyTurn = role !== 'spectator' && 
                   ((gameState.xIsNext && role === 'X') || 
                    (!gameState.xIsNext && role === 'O'));

  return (
    <div style={{ textAlign: 'center', marginTop: '30px' }}>
      <h1>Multiplayer Tic-Tac-Toe</h1>
      
      <div style={{ marginBottom: '20px' }}>
        <strong>Match Code: {matchCode}</strong>
        <div>Your Role: <strong>{role === 'spectator' ? 'Spectator 👁️' : `Player ${role}`}</strong></div>
        {isMyTurn && <div style={{ color: 'green', fontWeight: 'bold' }}>Your Turn!</div>}
      </div>

      <div className="status" style={{ fontSize: '20px', marginBottom: '20px' }}>
        {status}
      </div>

      <div className="board" style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 100px)',
        gap: '5px',
        justifyContent: 'center',
        marginBottom: '20px'
      }}>
        {gameState.board.map((cell, i) => (
          <button
            key={i}
            onClick={() => handleClick(i)}
            style={{
              width: '100px',
              height: '100px',
              fontSize: '32px',
              fontWeight: 'bold',
              cursor: role === 'spectator' || !isMyTurn ? 'not-allowed' : 'pointer',
              backgroundColor: cell ? '#e0e0e0' : 'white'
            }}
            disabled={role === 'spectator' || !isMyTurn}
          >
            {cell}
          </button>
        ))}
      </div>

      {role !== 'spectator' && (
        <button onClick={restartGame} style={{ fontSize: '16px', padding: '10px 20px' }}>
          Restart Game
        </button>
      )}

      <div style={{ marginTop: '20px', fontSize: '14px', color: '#666' }}>
        <div>Player X: {gameState.players.X ? '✓' : 'Waiting...'}</div>
        <div>Player O: {gameState.players.O ? '✓' : 'Waiting...'}</div>
        <div>Spectators: {gameState.spectators.length}</div>
      </div>
    </div>
  );
}

export default App;