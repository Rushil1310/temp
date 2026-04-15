let challengerUid = null;
let statusTimeout = null;
const ws = new WebSocket(`ws://${location.host}/ws/lobby`);
ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.type === "lobby_update") {
        document.getElementById("players").innerHTML = 
            msg.users.map(u => {
                if (u.uid === uid) {
                    return `<div style="border-color: var(--neon-cyan); box-shadow: 0 0 5px var(--neon-cyan); cursor: default;">${u.name} (You)</div>`;
                }
                return `<div onclick="challenge('${u.uid}')">Challenge: ${u.name}</div>`
            }).join("");
    }
    if (msg.type === "challenge_sent") {
        setStatus(`Challenge sent to ${msg.to_name}!`);
    }
    if (msg.type === "challenge_incoming") {
        challengerUid = msg.from_uid;
        document.getElementById("modal-msg").textContent = 
            `${msg.from_name} wants to play!`;
        document.getElementById("modal").style.display = "block";
    }
    if (msg.type === "challenge_declined") {
        setStatus(`${msg.by_name} declined your challenge.`);
    }
    if (msg.type === "redirect_to_game") {
        location.href = `/game/${msg.room_id}`;
    }
    if (msg.type === "error") {
        document.body.innerHTML = `
            <div class="container" style="margin-top: 50px;">
                <h1 style="color: var(--neon-pink); text-shadow: 0 0 15px var(--neon-pink);">DISCONNECTED</h1>
                <p style="font-size: 1.2rem;">${msg.message}</p>
                <p>Please close this tab.</p>
            </div>
        `;
        ws.close();
    }
};

function challenge(toUid) {
    ws.send(JSON.stringify({ type: "challenge", to_uid: toUid }));
}

function respond(accept) {
    ws.send(JSON.stringify({ type: "challenge_response", accept: accept, to_uid: challengerUid }));
    document.getElementById("modal").style.display = "none";
}

function setStatus(message) {
    document.getElementById("status").textContent = message;
    if (statusTimeout) clearTimeout(statusTimeout);
    statusTimeout = setTimeout(() => {
        document.getElementById("status").textContent = "";
        statusTimeout = null;
    }, 3000);
}

function goToLeaderboard() {
    window.location.href = "/leaderboard";
}