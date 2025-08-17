# RL_2048_agent

This repository contains the backend API (`api.js`) and a Python reinforcement learning agent (`agent.py`) to automate and analyze 2048 game play. It is designed to work closely with the frontend React 2048 game project (see your `src` folder from [React_2048_game](https://github.com/yuvnahr/React_2048_game)), allowing seamless connection and experimentation with AI-driven moves.

---

## Contents

- `api.js` — A Node.js/Express API backend that simulates the 2048 game and exposes endpoints for state management and moves.
- `agent.py` — A Python RL agent that makes intelligent moves by communicating with the API and learning from experience.
- `README.md` — This documentation.
- `LICENSE` — Project license.
- `.gitignore` — Ignores node_modules, Python cache, and virtual environments.

---

## How it Works

- **api.js**:  
  This file sets up a REST API server that mimics the 2048 game board. It creates endpoints such as `/reset` (restart the board), `/state` (get board and score), and `/move` (execute a move in a direction). The API maintains a game state in memory and interacts with the RL agent or any client over HTTP.

- **agent.py**:  
  This Python file is an RL agent that sends HTTP requests to the API server to reset the board, retrieve the state, and make moves. It uses lookahead and heuristics to select the best action. The agent learns by interacting with the API repeatedly, collecting experience and statistics.

- **Dependency on src (React frontend)**:  
  While the RL agent and API can run independently, the React frontend (from your other repository) can also connect to the API for scoring, move automation, or extended features, giving you a hybrid AI/game experience.

---

## Getting Started

### 1. **Clone this repository**

git clone https://github.com/yuvnahr/RL_2048_agent.git

cd RL_2048_agent

### 2. **Install Node.js dependencies for the API**
npm install

*(If you do not see package.json, you may need to run `npm init` and add express as a dependency: `npm install express`)*

### 3. **Run the API server**
node api.js

- The API will typically listen on `http://localhost:4000`.

### 4. **Set up Python for the RL agent**

- Install Python 3.x if not already installed.
- Install required dependencies:

pip install requests

### 5. **Run the RL agent**
python agent.py

- The agent will connect to `http://localhost:4000`, control the game, and print results to the console.

### 6. **Connecting with the React Frontend**

- If you want your frontend to use the API, point its backend requests (if configured in your React project, e.g., fetch or axios calls) to `http://localhost:4000`.
- For fully automated play, the RL agent runs moves and you can visualize the board in React by syncing the state.
- Both the agent and `src` app can control/reset/read the same API server.

---

## Save and Connect Your Files

- Place `api.js` and `agent.py` in a local project folder (e.g., `RL_2048_agent`).
- Make sure your React project is in a separate folder (as [React_2048_game](https://github.com/yuvnahr/React_2048_game)), with `src` containing the UI logic.
- Both projects should run at the same time for integration and testing.

---

## Useful Tips

- Ensure `api.js` is always running before starting `agent.py`.
- Default ports/settings should match in both projects (`http://localhost:4000`).
- To see results visually, fetch the game state from API in your frontend after each agent move.

---

## License

MIT License. See `LICENSE` for details.

---

Explore, modify, and connect your AI agent with your 2048 game frontend for research and experiments!

