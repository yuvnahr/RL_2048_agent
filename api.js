import express from 'express';
import cors from 'cors';
// Import specific named exports from your game.js
import {
  SIZE,
  emptyBoard,
  cloneBoard,
  addRandomTile,
  move,
  hasMoves,
  highestTile,
} from './game.js'; // Use correct relative path if needed

const app = express();
const PORT = 4000;

app.use(express.json());
app.use(cors());

// Initialize game state variables
let board = addRandomTile(addRandomTile(emptyBoard()));
let score = 0;

/**
 * GET /state
 * Returns the current game board, score, highest tile, and whether moves are possible
 */
app.get('/state', (req, res) => {
  res.json({
    board,
    score,
    highest: highestTile(board),
    canMove: hasMoves(board),
  });
});

/**
 * POST /move
 * Body: { direction: 'up' | 'down' | 'left' | 'right' }
 * Makes a move and returns updated board, score, whether move was successful, and game over status
 */
app.post('/move', (req, res) => {
  const { direction } = req.body;

  if (!['up', 'down', 'left', 'right'].includes(direction)) {
    return res.status(400).json({ error: 'Invalid move direction' });
  }

  const { board: newBoard, score: gained, moved } = move(board, direction);

  if (!moved) {
    // Move did nothing, return current state and game over status
    return res.json({
      board,
      score,
      moved: false,
      gameOver: !hasMoves(board),
      highest: highestTile(board),
    });
  }

  // Add random tile after a successful move
  board = addRandomTile(newBoard);
  score += gained;

  res.json({
    board,
    score,
    moved: true,
    gameOver: !hasMoves(board),
    highest: highestTile(board),
  });
});

/**
 * POST /reset
 * Resets the game to a new initial state and returns that state
 */
app.post('/reset', (req, res) => {
  board = addRandomTile(addRandomTile(emptyBoard()));
  score = 0;
  res.json({
    board,
    score,
    highest: highestTile(board),
    canMove: true,
  });
});

// Start the API server
app.listen(PORT, () => {
  console.log(`RL API listening on port ${PORT}`);
});
