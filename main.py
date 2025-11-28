from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from typing import Dict, Set
import json
import uuid
from game_manager import game_manager
from models import JoinRoomRequest, SubmitAnswerRequest, HostActionRequest, ConfigureGameRequest, VoteRequest


app = FastAPI(title="Trivia Night")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        # room_code -> set of websockets
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_code: str):
        await websocket.accept()
        if room_code not in self.active_connections:
            self.active_connections[room_code] = set()
        self.active_connections[room_code].add(websocket)

    def disconnect(self, websocket: WebSocket, room_code: str):
        if room_code in self.active_connections:
            self.active_connections[room_code].discard(websocket)
            if not self.active_connections[room_code]:
                del self.active_connections[room_code]

    async def broadcast(self, room_code: str, message: dict):
        """Broadcast message to all connections in a room"""
        if room_code in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[room_code]:
                try:
                    await connection.send_json(message)
                except:
                    disconnected.add(connection)

            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections[room_code].discard(conn)


manager = ConnectionManager()


# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def read_root():
    """Serve the host/main display"""
    return FileResponse("static/index.html")


@app.get("/play")
async def read_play():
    """Serve the player interface"""
    return FileResponse("static/player.html")


@app.post("/api/create-room")
async def create_room():
    """Create a new game room"""
    host_id = str(uuid.uuid4())
    room_code = game_manager.create_room(host_id)
    return {
        "room_code": room_code,
        "host_id": host_id
    }


@app.post("/api/join-room")
async def join_room(request: JoinRoomRequest):
    """Join an existing room"""
    player_id = str(uuid.uuid4())
    success = game_manager.add_player(
        request.room_code,
        player_id,
        request.player_name
    )

    if not success:
        raise HTTPException(status_code=400, detail="Could not join room")

    # Broadcast updated game state
    room = game_manager.get_room(request.room_code)
    if room:
        await manager.broadcast(request.room_code, {
            "type": "state_update",
            "state": room.model_dump(mode='json')
        })

    return {
        "player_id": player_id,
        "room_code": request.room_code
    }


@app.post("/api/submit-answer")
async def submit_answer(request: SubmitAnswerRequest):
    """Submit an answer"""
    success = game_manager.submit_answer(
        request.room_code,
        request.player_id,
        request.answer
    )

    if not success:
        raise HTTPException(status_code=400, detail="Could not submit answer")

    # Broadcast updated game state
    room = game_manager.get_room(request.room_code)
    if room:
        await manager.broadcast(request.room_code, {
            "type": "state_update",
            "state": room.model_dump(mode='json')
        })

    return {"success": True}


@app.post("/api/configure-game")
async def configure_game(request: ConfigureGameRequest):
    """Configure game settings"""
    success = game_manager.configure_game(
        request.room_code,
        request.num_questions,
        request.difficulty,
        request.include_final_hard_question
    )

    if not success:
        raise HTTPException(status_code=400, detail="Could not configure game")

    # Broadcast updated game state
    room = game_manager.get_room(request.room_code)
    if room:
        await manager.broadcast(request.room_code, {
            "type": "state_update",
            "state": room.model_dump(mode='json')
        })

    return {"success": True}


@app.post("/api/vote")
async def vote(request: VoteRequest):
    """Submit a vote for a disputed answer"""
    success = game_manager.submit_vote(
        request.room_code,
        request.player_id,
        request.judgement_index,
        request.vote
    )

    if not success:
        raise HTTPException(status_code=400, detail="Could not submit vote")

    # Broadcast updated game state
    room = game_manager.get_room(request.room_code)
    if room:
        await manager.broadcast(request.room_code, {
            "type": "state_update",
            "state": room.model_dump(mode='json')
        })

    return {"success": True}


@app.post("/api/host-action")
async def host_action(request: HostActionRequest):
    """Handle host actions like starting game, next question, etc."""
    room = game_manager.get_room(request.room_code)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    if request.action == "start_game":
        game_manager.start_game(request.room_code)
    elif request.action == "start_answering":
        game_manager.start_answering(request.room_code)
    elif request.action == "judge_answers":
        await game_manager.judge_answers(request.room_code)
    elif request.action == "start_voting":
        # Get judgement index from request data if provided
        # For now, we'll need to pass it through a custom field
        pass  # This will be handled by a separate endpoint
    elif request.action == "finish_voting":
        game_manager.finish_voting(request.room_code)
    elif request.action == "next_question":
        game_manager.next_question(request.room_code)
    else:
        raise HTTPException(status_code=400, detail="Unknown action")

    # Broadcast updated game state
    room = game_manager.get_room(request.room_code)
    if room:
        await manager.broadcast(request.room_code, {
            "type": "state_update",
            "state": room.model_dump(mode='json')
        })

    return {"success": True}


@app.post("/api/start-voting/{room_code}/{judgement_index}")
async def start_voting(room_code: str, judgement_index: int):
    """Start a vote on a disputed answer"""
    success = game_manager.start_voting(room_code, judgement_index)

    if not success:
        raise HTTPException(status_code=400, detail="Could not start voting")

    # Broadcast updated game state
    room = game_manager.get_room(room_code)
    if room:
        await manager.broadcast(room_code, {
            "type": "state_update",
            "state": room.model_dump(mode='json')
        })

    return {"success": True}


@app.websocket("/ws/{room_code}")
async def websocket_endpoint(websocket: WebSocket, room_code: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, room_code)

    try:
        # Send initial state
        room = game_manager.get_room(room_code)
        if room:
            await websocket.send_json({
                "type": "state_update",
                "state": room.model_dump(mode='json')
            })

        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            # Could handle client messages here if needed

    except WebSocketDisconnect:
        manager.disconnect(websocket, room_code)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
