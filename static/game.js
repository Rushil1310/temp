let mySymbol = null;
let gameOver = false;
const ws = new WebSocket(`ws://${location.host}/ws/game/${roomId}`);
function returnToLobby() {
    window.location.href = `/lobby`;
}
ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);

    if (msg.type === "game_init") {
        mySymbol = msg.symbol;
        document.getElementById("info").textContent = 
            `You are ${mySymbol} · vs ${msg.opponent_name}`;
        renderBoard(msg.board, msg.turn_uid);
    }

    if (msg.type === "board_update") {
        renderBoard(msg.board, msg.turn_uid);
    }

    if (msg.type === "game_over") {
        renderBoard(msg.board, null);
        gameOver = true;
        if (msg.winner === "draw") {
            document.getElementById("result").textContent = "It's a draw!";
        } else if (msg.winner_uid === uid) {
            document.getElementById("result").textContent = "VICTORY!";
        } else {
            document.getElementById("result").textContent = "DEFEAT.";
            document.getElementById("result").style.color = "red";
            document.getElementById("result").style.textShadow = "0 0 8px red";
        }
        document.getElementById("turn-info").textContent = "";
        document.getElementById("back-btn").style.display = "inline-block";
    }

    if (msg.type === "opponent_left") {
        if (!gameOver) {
            gameOver = true;
            document.getElementById("result").textContent = "Opponent disconnected — you win!";
            document.getElementById("back-btn").style.display = "inline-block";
        }
    }
};

function renderBoard(board, turnUid) {
    const cells = document.querySelectorAll(".cell");
    board.forEach((val, i) => {
        cells[i].textContent = val;
        
        // Add conditional coloring for X and 0 (optional purely aesthetic tweak that doesn't break logic)
        if(val === "X") { cells[i].style.color = "var(--neon-pink)"; cells[i].style.textShadow = "0 0 10px var(--neon-pink)"; }
        if(val === "0") { cells[i].style.color = "var(--neon-green)"; cells[i].style.textShadow = "0 0 10px var(--neon-green)"; }
        
        cells[i].onclick = val || gameOver ? null : () => makeMove(i);
    });
    if (turnUid && !gameOver) {
        document.getElementById("turn-info").textContent = 
            turnUid === uid ? "> Your turn <" : "Waiting for opponent...";
    }
}

function makeMove(index) {
    if (gameOver) return;
    console.log(index);
    ws.send(JSON.stringify({ type: "move", index }));
}


