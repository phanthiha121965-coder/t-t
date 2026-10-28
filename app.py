from flask import Flask, render_template_string, request, jsonify, session
from flask_socketio import SocketIO, emit
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tet_dinh_mui_2027_dungdepzai_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

users_db = {}       
messages_db = []    
ADMIN_USER = "dunghoet"
ADMIN_PASS = "10091990dung"

@app.route('/')
def home():
    return render_template_string(HTML_CODE)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    u = data.get('username', '').strip()
    p = data.get('password', '').strip()
    if not u or not p:
        return jsonify({"success": False, "msg": "Nhập thiếu thông tin kìa!"})
    if u not in users_db:
        users_db[u] = {"password": p, "streak": 0, "last_checkin": None}
    elif users_db[u]["password"] != p:
        return jsonify({"success": False, "msg": "Sai mật khẩu rồi!"})
    session['user'] = u
    return jsonify({"success": True, "username": u, "user_data": users_db[u]})

@app.route('/api/checkin', methods=['POST'])
def checkin():
    user = session.get('user')
    if not user or user not in users_db:
        return jsonify({"success": False, "msg": "Chưa đăng nhập!"})
    today = str(datetime.date.today())
    udata = users_db[user]
    if udata["last_checkin"] == today:
        return jsonify({"success": False, "msg": "Hôm nay đã điểm danh rồi!"})
    udata["streak"] += 1
    udata["last_checkin"] = today
    return jsonify({"success": True, "msg": f"Điểm danh thành công! Streak: {udata['streak']} ngày 🔥", "streak": udata['streak']})

@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.json or {}
    if data.get('username') == ADMIN_USER and data.get('password') == ADMIN_PASS:
        session['is_admin'] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "msg": "Sai tài khoản hoặc mật khẩu Admin!"})

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return "<h3>Truy cập bị từ chối! Bấm 10 lần vào nút điểm danh ngoài trang chủ để đăng nhập.</h3>", 403
    return render_template_string(ADMIN_HTML, users=users_db, msg_count=len(messages_db))

@socketio.on('send_message')
def handle_message(data):
    user = session.get('user', 'Khách ẩn danh')
    text = (data or {}).get('message', '').strip()
    if text:
        msg = {"user": user, "text": text, "time": datetime.datetime.now().strftime("%H:%M")}
        messages_db.append(msg)
        if len(messages_db) >= 1000:
            del messages_db[:500]
        emit('receive_message', msg, broadcast=True)

@socketio.on('connect')
def handle_connect():
    emit('load_history', messages_db)

HTML_CODE = """<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tết Đinh Mùi 2027 - Dũng Đẹp Trai</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body { font-family: sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 15px; }
        .card { background: #0a0a0a; border: 1px solid rgba(248,181,0,0.4); border-radius: 16px; padding: 18px; margin: 12px auto; max-width: 400px; box-shadow: 0 0 20px rgba(248,181,0,0.1); }
        .btn { background: linear-gradient(135deg, #f8b500, #d4af37); color: #000; font-weight: bold; padding: 12px; border-radius: 25px; border: none; width: 100%; max-width: 280px; cursor: pointer; margin-top: 8px; font-size: 14px; text-transform: uppercase; }
        .timer { font-size: 18px; font-weight: bold; color: #f8b500; background: #111; padding: 10px; border-radius: 10px; border: 1px dashed #d4af37; }
        input { background: #111; color: #f8b500; border: 1px solid #d4af37; padding: 10px; border-radius: 8px; width: calc(100% - 20px); max-width: 260px; margin: 6px 0; text-align: center; outline: none; }
        #chat-box { height: 160px; overflow-y: scroll; background: #050505; text-align: left; padding: 10px; border-radius: 8px; border: 1px solid #333; margin-bottom: 10px; }
        .msg { font-size: 13px; margin-bottom: 6px; border-bottom: 1px solid #111; padding-bottom: 4px; word-break: break-word; }
        .msg b { color: #f8b500; }
        #modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 999; justify-content: center; align-items: center; }
        .modal-content { background: #0a0a0a; padding: 20px; border-radius: 15px; border: 2px solid #f8b500; width: 85%; max-width: 300px; }
        #music-btn { position: fixed; bottom: 15px; right: 15px; z-index: 99; background: #f8b500; color: #000; border: none; padding: 10px 16px; border-radius: 20px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div style="font-size:28px;">🏮</div>
    <h2 style="color:#f8b500; margin:5px 0;">TẾT ĐINH MÙI 2027</h2>
    <div style="font-size:12px; color:#d4af37; margin-bottom:12px;">Mùng 1 Tết: 06/02/2027 (Dương Lịch)</div>

    <div class="card">
        <div class="timer" id="timer">Đang tải thời gian...</div>
    </div>

    <div class="card">
        <div id="auth-box">
            <h3 style="color:#f8b500; margin-top:0;">🔑 Đăng Nhập</h3>
            <input type="text" id="u" placeholder="Tài khoản"><br>
            <input type="password" id="p" placeholder="Mật khẩu"><br>
            <button class="btn" onclick="login()">Vào Web</button>
        </div>
        <div id="user-box" style="display:none;">
            <h3 style="color:#f8b500; margin-top:0;">Chào, <span id="uname"></span>!</h3>
            <p>🔥 Streak: <b id="streak" style="color:#ff3333;">0</b> ngày</p>
            <button class="btn" onclick="checkin()">✨ Điểm Danh Hôm Nay ✨</button>
        </div>
    </div>

    <div class="card">
        <h3 style="color:#f8b500; margin-top:0;">💬 Khung Chat</h3>
        <div id="chat-box"></div>
        <div style="display:flex; gap:5px; justify-content:center;">
            <input type="text" id="msg" placeholder="Nhập tin nhắn..." style="flex:1; margin:0;">
            <button class="btn" onclick="send()" style="width:auto; padding:10px 15px; margin:0;">Gửi</button>
        </div>
    </div>

    <div id="modal">
        <div class="modal-content">
            <h3 style="color:#f8b500; margin-top:0;">🔒 Admin</h3>
            <input type="text" id="au" placeholder="TK Admin"><br>
            <input type="password" id="ap" placeholder="MK Admin"><br><br>
            <button class="btn" onclick="adminLogin()">Đăng Nhập</button>
            <button class="btn" onclick="document.getElementById('modal').style.display='none'" style="background:#333; color:#fff; margin-top:5px;">Đóng</button>
        </div>
    </div>

    <iframe id="yt" width="0" height="0" src="https://www.youtube.com/embed/n8l_j0UKT3Y?autoplay=1&loop=1&playlist=n8l_j0UKT3Y" frameborder="0" allow="autoplay"></iframe>
    <button onclick="toggleMusic()" id="music-btn">🎵 Tắt Nhạc</button>

    <script>
        const tet = new Date("Feb 6, 2027 00:00:00").getTime();
        setInterval(() => {
            const now = new Date().getTime();
            const d = tet - now;
            if(d > 0) {
                const days = Math.floor(d / (1000 * 60 * 60 * 24));
                const hours = Math.floor((d % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const mins = Math.floor((d % (1000 * 60 * 60)) / (1000 * 60));
                const secs = Math.floor((d % (1000 * 60)) / 1000);
                document.getElementById("timer").innerHTML = `${days}N ${hours}G ${mins}P ${secs}G`;
            } else {
                document.getElementById("timer").innerHTML = "🎉 CHÚC MỪNG NĂM MỚI 2027 🎉";
            }
        }, 1000);

        let count = 0, t = null;
        async function login() {
            const res = await fetch('/api/login', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:document.getElementById('u').value, password:document.getElementById('p').value})});
            const data = await res.json();
            if(data.success) {
                document.getElementById('auth-box').style.display = 'none';
                document.getElementById('user-box').style.display = 'block';
                document.getElementById('uname').innerText = data.username;
                document.getElementById('streak').innerText = data.user_data.streak;
            } else { alert(data.msg); }
        }

        async function checkin() {
            count++; clearTimeout(t);
            if(count >= 10) { count = 0; document.getElementById('modal').style.display = 'flex'; return; }
            t = setTimeout(() => { count = 0; }, 3000);

            const res = await fetch('/api/checkin', {method:'POST'});
            const data = await res.json();
            alert(data.msg);
            if(data.success) document.getElementById('streak').innerText = data.streak;
        }

        async function adminLogin() {
            const res = await fetch('/admin-login', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:document.getElementById('au').value, password:document.getElementById('ap').value})});
            const data = await res.json();
            if(data.success) { window.location.href = '/admin'; } else { alert(data.msg); }
        }

        const socket = io();
        const chatBox = document.getElementById('chat-box');
        socket.on('load_history', (msgs) => { chatBox.innerHTML = ''; msgs.forEach(m => addMsg(m)); });
        socket.on('receive_message', (m) => { addMsg(m); });

        function send() {
            const inp = document.getElementById('msg');
            if(inp.value.trim() !== "") { socket.emit('send_message', {message: inp.value}); inp.value = ''; }
        }
        document.getElementById('msg').addEventListener('keypress', (e) => { if(e.key === 'Enter') send(); });

        function addMsg(m) {
            const div = document.createElement('div');
            div.className = 'msg';
            div.innerHTML = `<b>[${m.time}] ${m.user}:</b> ${m.text}`;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        let play = true;
        function toggleMusic() {
            const yt = document.getElementById('yt');
            const btn = document.getElementById('music-btn');
            if(play) { yt.src = ''; btn.innerText = '🎵 Bật Nhạc'; play = false; }
            else { yt.src = 'https://www.youtube.com/embed/n8l_j0UKT3Y?autoplay=1&loop=1&playlist=n8l_j0UKT3Y'; btn.innerText = '🎵 Tắt Nhạc'; play = true; }
        }
    </script>
</body>
</html>"""

ADMIN_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Admin</title>
<style>
    body { font-family:sans-serif; background:#000; color:#f8b500; padding:20px; }
    table { width:100%; border-collapse:collapse; background:#0a0a0a; margin-top:15px; border:1px solid #d4af37; border-radius:8px; overflow:hidden; }
    th, td { border:1px solid #333; padding:10px; text-align:left; font-size:14px; }
    th { background:#d4af37; color:#000; }
    .card { background:#0a0a0a; padding:15px; border-radius:10px; border:1px solid #d4af37; }
    a { color:#f8b500; font-weight:bold; text-decoration:none; }
</style>
</head>
<body>
    <div class="card">
        <h2>📊 Quản Trị Hệ Thống</h2>
        <p>Tổng tin nhắn: <b>{{ msg_count }} / 1000</b></p>
        <p><a href="/">⬅ Về trang chủ</a></p>
    </div>
    <h3 style="color:#fff; margin-top:20px;">Danh sách người dùng</h3>
    <table>
        <tr><th>Tài khoản</th><th>Streak</th><th>Điểm danh gần nhất</th></tr>
        {% for u, d in users.items() %}
        <tr>
            <td><b>{{ u }}</b></td>
            <td>{{ d.streak }} ngày 🔥</td>
            <td>{{ d.last_checkin or 'Chưa' }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>"""

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
