import os
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room

app = Flask(__name__)
app.config['SECRET_KEY'] = 'atif_video_secret_2026'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    emit('user-joined', request.sid, room=room, include_self=False)

@socketio.on('offer')
def handle_offer(data):
    emit('offer', {'sdp': data['sdp'], 'sender': request.sid}, to=data['target'])

@socketio.on('answer')
def handle_answer(data):
    emit('answer', {'sdp': data['sdp'], 'sender': request.sid}, to=data['target'])

@socketio.on('ice-candidate')
def handle_ice(data):
    emit('ice-candidate', {'candidate': data['candidate'], 'sender': request.sid}, to=data['target'])

@socketio.on('disconnect')
def handle_disconnect():
    emit('user-left', request.sid, broadcast=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port)
