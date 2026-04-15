from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Form, HTTPException # type: ignore
from fastapi.responses import HTMLResponse, RedirectResponse # type: ignore
from fastapi.templating import Jinja2Templates # type: ignore
from fastapi.staticfiles import StaticFiles # type: ignore
from starlette.middleware.sessions import SessionMiddleware # type: ignore
from dotenv import load_dotenv #type: ignore

import os
import json
import asyncio
import sqlite3

load_dotenv()

app = FastAPI()

seshSecret = os.getenv("SECRET_KEY", "fallback_dev_key")

app.add_middleware(SessionMiddleware, secret_key=seshSecret)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def update_elo(r1, r2, result):
    K = 32
    
    E1 = 1 / (1 + 10 ** ((r2 - r1) / 400))
    E2 = 1 / (1 + 10 ** ((r1 - r2) / 400))
    
    if result == 1:       # player1 wins
        S1, S2 = 1, 0
    elif result == 0:     # player2 wins
        S1, S2 = 0, 1
    else:                 # draw
        S1 = S2 = 0.5

    new_r1 = r1 + K * (S1 - E1)
    new_r2 = r2 + K * (S2 - E2)

    return int(new_r1), int(new_r2)

def load_users():
    users = {}
    try:
        conn = sqlite3.connect("database.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT uid, name, elo_rating, is_online FROM users")
        rows = cursor.fetchall()
        
        for row in rows:
            uid = row["uid"]
            users[uid] = {
                "name": row["name"],
                "elo": row["elo_rating"],
                "is_online": bool(row["is_online"])
            }
        
        conn.close()
    except sqlite3.OperationalError as e:
        print(f"Error loading users from database: {e}")
    
    return users

def check_winner(board):
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b,c in wins:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if all(board):
        return "draw"
    return None

users = load_users()

online: dict[str, WebSocket] = {}
rooms: dict[str, dict] = {}
pending_challenges: dict[str, dict] = {}

@app.get("/")
async def root():
    return RedirectResponse("/login")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.post("/login")
async def do_login(request: Request, name: str = Form(...)):
    uid = name.strip().lower().replace(" ", "_")
    if uid not in users:
        return RedirectResponse("/login?error=User+not+found", status_code=303)
    users[uid]["is_online"] = True

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET is_online = 1 WHERE uid = ?", (uid,))
    conn.commit()
    conn.close()

    request.session["uid"] = uid
    
    return RedirectResponse("/lobby", status_code=303)

@app.get("/lobby", response_class=HTMLResponse)
async def lobby_page(request: Request):
    uid = request.session.get("uid")
    if uid not in users:
        return RedirectResponse("/login")
    return templates.TemplateResponse(request, "lobby.html", {"uid": uid, "name": users[uid]["name"]})

async def broadcast_lobby():
    payload = json.dumps({
        "type": "lobby_update",
        "users": [
            {"uid": uid, "name": users[uid]["name"], "elo": users[uid]["elo"]}
            for uid in online
        ]
    })
    for uid, ws in list(online.items()):
        try:
            await ws.send_text(payload)
        except Exception:
            online.pop(uid, None)

@app.get("/logout")
async def logout(request: Request):
    uid = request.session.get("uid")
    if uid and uid in users:
        users[uid]["is_online"] = False
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_online = 0 WHERE uid = ?", (uid,))
        conn.commit()
        conn.close()
    request.session.clear()
    return RedirectResponse("/login", status_code=303)

@app.websocket("/ws/lobby")
async def lobby_ws(websocket: WebSocket):
    await websocket.accept()
    uid = websocket.session.get("uid")
    if not uid or uid not in users:
        await websocket.close()
        return

    if uid in online:
        old_ws = online[uid]
        try:
            await old_ws.send_text(json.dumps({
                "type": "error",
                "message": "Session disconnected: Logged in from another location."
            }))
            await old_ws.close()
        except Exception:
            pass

    online[uid] = websocket
    await broadcast_lobby()

    try:
        while True:
            data = json.loads(await websocket.receive_text())
            
            if data["type"] == "challenge":
                to_uid = data["to_uid"]
                if to_uid in online:
                    await online[uid].send_text(json.dumps({
                        "type": "challenge_sent",
                        "to_name": users[data["to_uid"]]["name"]
                    }))
                    await online[to_uid].send_text(json.dumps({
                        "type": "challenge_incoming",
                        "from_uid": uid,
                        "from_name": users[uid]["name"]
                    }))
            elif data["type"] == "challenge_response":
                challenger_uid = data["to_uid"]
                accept = data["accept"]

                if not accept:
                    if challenger_uid in online:
                        await online[challenger_uid].send_text(json.dumps({
                            "type": "challenge_declined",
                            "by_name": users[uid]["name"]
                        }))
                else:
                    room_id = f"{challenger_uid}_vs_{uid}"
                    rooms[room_id] = {
                        "players": [challenger_uid, uid],
                        "symbols": {challenger_uid: "X", uid: "O"},
                        "board": [""] * 9,
                        "turn": challenger_uid,
                        "sockets": {}
                    }
                    for p_uid in [challenger_uid, uid]:
                        if p_uid in online:
                            await online[p_uid].send_text(json.dumps({
                                "type": "redirect_to_game",
                                "room_id": room_id
                            }))
    except WebSocketDisconnect:
        if online.get(uid) == websocket:
            online.pop(uid, None)
            users[uid]["is_online"] = False
            await broadcast_lobby()

@app.get("/game/{room_id}", response_class=HTMLResponse)
async def game_page(request: Request, room_id: str):
    uid = request.session.get("uid")
    if room_id not in rooms or uid not in users:
        return RedirectResponse("/login")
    return templates.TemplateResponse(request, "game.html", {"uid": uid, "room_id": room_id})


@app.websocket("/ws/game/{room_id}")
async def game_ws(websocket: WebSocket, room_id: str):
    await websocket.accept()
    uid = websocket.session.get("uid")

    if room_id not in rooms or uid not in rooms[room_id]["players"]:
        await websocket.close()
        return

    room = rooms[room_id]
    room["sockets"][uid] = websocket

    if len(room["sockets"]) == 2:
        for p_uid, p_ws in room["sockets"].items():
            opponent_uid = [x for x in room["players"] if x != p_uid][0]
            await p_ws.send_text(json.dumps({
                "type": "game_init",
                "symbol": room["symbols"][p_uid],
                "opponent_name": users[opponent_uid]["name"],
                "board": room["board"],
                "turn_uid": room["turn"]
            }))

    try:
        while True:
            data = json.loads(await websocket.receive_text())

            if data["type"] == "move":
                index = data["index"]
                if room["turn"] != uid or not (0 <= index <= 8) or room["board"][index] != "":
                    continue

                room["board"][index] = room["symbols"][uid]
                result = check_winner(room["board"])

                if result:
                    p1, p2 = room["players"]

                    r1 = users[p1]["elo"]
                    r2 = users[p2]["elo"]

                    if result == "draw":
                        new_r1, new_r2 = update_elo(r1, r2, 0.5)
                    elif result == room["symbols"][p1]:
                        new_r1, new_r2 = update_elo(r1, r2, 1)
                    else:
                        new_r1, new_r2 = update_elo(r1, r2, 0)

                    # update memory
                    users[p1]["elo"] = new_r1
                    users[p2]["elo"] = new_r2

                    # update DB
                    conn = sqlite3.connect("database.db")
                    cursor = conn.cursor()
                    cursor.execute("UPDATE users SET elo_rating=? WHERE uid=?", (new_r1, p1))
                    cursor.execute("UPDATE users SET elo_rating=? WHERE uid=?", (new_r2, p2))
                    conn.commit()
                    conn.close()

                    payload = {
                        "type": "game_over",
                        "board": room["board"],
                        "winner": result,
                        "winner_uid": uid if result != "draw" else None
                    }
                    for p_ws in room["sockets"].values():
                        await p_ws.send_text(json.dumps(payload))
                else:
                    other = [x for x in room["players"] if x != uid][0]
                    room["turn"] = other
                    for p_ws in room["sockets"].values():
                        await p_ws.send_text(json.dumps({
                            "type": "board_update",
                            "board": room["board"],
                            "turn_uid": room["turn"]
                        }))

    except WebSocketDisconnect:
        if room["sockets"].get(uid) == websocket:
            room["sockets"].pop(uid, None)
            for p_ws in room["sockets"].values():
                await p_ws.send_text(json.dumps({"type": "opponent_left"}))
            await asyncio.sleep(5)
            rooms.pop(room_id, None)

@app.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard(request: Request):
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT name, elo_rating FROM users ORDER BY elo_rating DESC")
    players = cursor.fetchall()

    conn.close()

    return templates.TemplateResponse(
        request,
        "leaderboard.html",
        {"players": players}
    )

@app.get("/me")
def getMe(request: Request):
    uid = request.session.get("uid")
    if not uid:
        raise HTTPException(
            status_code = 404,
            detail = "Unverified User"
        ) 
    else:
        return({"uid":uid})