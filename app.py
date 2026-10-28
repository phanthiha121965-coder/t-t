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
    return render_template_string(FULL_HTML_TEMPLATE)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    if not username or not password:
        return jsonify({"success": False, "msg": "Nhập thiếu thông tin kìa ông giáo ơi!"})
    if username not in users_db:
        users_db[username] = {"password": password, "streak": 0, "last_checkin": None}
    elif users_db[username]["password"] != password:
        return jsonify({"success": False, "msg": "Sai mật khẩu rồi!"})
    session['user'] = username
    return jsonify({"success": True, "username": username, "user_data": users_db[username]})

@app.route('/api/checkin', methods=['POST'])
def checkin():
    user = session.get('user')
    if not user or user not in users_db:
        return jsonify({"success": False, "msg": "Chưa đăng nhập mà đòi điểm danh hả :v"})
    today = str(datetime.date.today())
    udata = users_db[user]
    if udata["last_checkin"] == today:
        return jsonify({"success": False, "msg": "Hôm nay điểm danh rồi, mai vào lại nhé!"})
    udata["streak"] += 1
    udata["last_checkin"] = today
    return jsonify({"success": True, "msg": f"Điểm danh thành công! Streak: {udata['streak']} ngày 🔥", "streak": udata['streak']})

@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.json
    if data.get('username') == ADMIN_USER and data.get('password') == ADMIN_PASS:
        session['is_admin'] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "msg": "Sai tài khoản hoặc mật khẩu Admin!"})

@app.route('/admin', methods=['GET'])
def admin():
    if not session.get('is_admin'):
        return "<h3>Truy cập bị từ chối! Bấm 10 lần vào nút điểm danh để mở trang đăng nhập Admin.</h3>", 403
    return render_template_string(ADMIN_TEMPLATE, users=users_db, msg_count=len(messages_db))

@socketio.on('send_message')
def handle_message(data):
    user = session.get('user', 'Khách ẩn danh')
    msg_text = data.get('message', '').strip()
    if msg_text:
        new_msg = {"user": user, "text": msg_text, "time": datetime.datetime.now().strftime("%H:%M")}
        messages_db.append(new_msg)
        if len(messages_db) >= 1000:
            del messages_db[:500]
        emit('receive_message', new_msg, broadcast=True)

@socketio.on('connect')
def handle_connect():
    emit('load_history', messages_db)

FULL_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đếm Ngược Tết 2027 - Dũng Đẹp Trai</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, sans-serif; background: linear-gradient(135deg, #2b0909, #0f0101); color: #fff; text-align: center; margin: 0; padding: 15px; }
        .box { background: rgba(26, 33, 62, 0.8); border-radius: 12px; padding: 15px; margin: 12px auto; max-width: 420px; box-shadow: 0 4px 20px rgba(0,0,0,0.6); border: 1px solid rgba(248,181,0,0.3); }
        h1 { color: #ff3333; font-size: 18px; text-transform: uppercase; margin-bottom: 5px; }
        #timer { font-size: 18px; font-weight: bold; color: #f8b500; margin: 8px 0; background: rgba(0,0,0,0.4); padding: 8px; border-radius: 8px; border: 1px dashed #f8b500; }
        input { background: #0f3460; color: #fff; border: 1px solid #e94560; width: calc(100% - 20px); max-width: 300px; padding: 10px; margin: 5px 0; border-radius: 6px; outline: none; }
        button { background: #e94560; color: white; cursor: pointer; font-weight: bold; padding: 10px 16px; margin: 5px 0; border-radius: 6px; border: none; font-size: 14px; }
        button:hover { background: #ff6b81; }
        #chat-box { height: 180px; overflow-y: scroll; background: #0f3460; text-align: left; padding: 10px; border-radius: 6px; margin-bottom: 8px; border: 1px solid #1f4068; }
        .msg { margin-bottom: 6px; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 4px; font-size: 13px; word-break: break-word; }
        .msg b { color: #f8b500; }
        #music-btn { position: fixed; bottom: 15px; right: 15px; z-index: 999; background: #f8b500; color: #1a0202; border: none; padding: 10px 16px; border-radius: 30px; cursor: pointer; font-weight: bold; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        #admin-modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 9999; justify-content: center; align-items: center; }
        .modal-content { background: #16213e; padding: 20px; border-radius: 12px; border: 2px solid #f8b500; width: 85%; max-width: 320px; text-align: center; }
    </style>
</head>
<body>
    <h1>🧨 ĐẾM NGƯỢC TẾT 2027 🧨</h1>
    <div style="color:#f8b500; font-size:12px; font-weight:bold; margin-bottom:10px;">👑 THƯƠNG HIỆU: DŨNG ĐẸP TRAI 👑</div>
    <div id="timer">Đang tính thời gian...</div>

    <div class="box">
        <div id="auth-section">
            <h3>🔑 Đăng nhập / Đăng ký</h3>
            <input type="text" id="username" placeholder="Tài khoản"><br>
            <input type="password" id="password" placeholder="Mật khẩu"><br>
            <button onclick="login()">Vào Web Ngay</button>
        </div>
        <div id="user-section" style="display:none;">
            <h3>Chào, <span id="user-display" style="color:#f8b500;"></span>!</h3>
            <p>🔥 Streak: <b id="streak-display" style="color:#e94560; font-size:16px;">0</b> ngày</p>
            <button onclick="handleCheckinClick()">Điểm Danh Hôm Nay</button>
        </div>
    </div>

    <div class="box">
        <h3 style="margin-top:0;">💬 Khung Chat Cộng Đồng</h3>
        <div id="chat-box"></div>
        <div style="display:flex; gap:5px; justify-content:center;">
            <input type="text" id="msg-input" placeholder="Nhập tin nhắn..." style="flex:1; margin:0;">
            <button onclick="sendMsg()" style="margin:0;">Gửi</button>
        </div>
    </div>

    <div id="admin-modal">
        <div class="modal-content">
            <h3 style="color:#e94560;">🔒 Đăng Nhập Admin</h3>
            <input type="text" id="admin-user" placeholder="Tài khoản Admin"><br>
            <input type="password" id="admin-pass" placeholder="Mật khẩu Admin"><br><br>
            <button onclick="submitAdminLogin()" style="width:100%;">Đăng Nhập</button>
            <button onclick="document.getElementById('admin-modal').style.display='none'" style="background:#555; width:100%; margin-top:5px;">Đóng</button>
        </div>
    </div>

    <iframe id="youtube-audio" width="0" height="0" src="https://www.youtube.com/embed/n8l_j0UKT3Y?autoplay=1&loop=1&playlist=n8l_j0UKT3Y" frameborder="0" allow="autoplay"></iframe>
    <button onclick="toggleYtMusic()" id="music-btn">🎵 Nhạc Tết</button>

    <script>
        const tetDate = new Date("Jan 29, 2027 00:00:00").getTime();
        setInterval(() => {
            const now = new Date().getTime();
            const d = tetDate - now;
            const days = Math.floor(d / (1000 * 60 * 60 * 24));
            const hours = Math.floor((d % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const mins = Math.floor((d % (1000 * 60 * 60)) / (1000 * 60));
            const secs = Math.floor((d % (1000 * 60)) / 1000);
            document.getElementById("timer").innerHTML = `${days}N ${hours}G ${mins}P ${secs}S`;
        }, 1000);

        let count = 0, timer = null;
        async function login() {
            const u = document.getElementById("username").value;
            const p = document.getElementById("password").value;
            const res = await fetch('/api/login', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username: u, password: p})});
            const data = await res.json();
            if (data.success) {
                document.getElementById("auth-section").style.display = "none";
                document.getElementById("user-section").style.display = "block";
                document.getElementById("user-display").innerText = data.username;
                document.getElementById("streak-display").innerText = data.user_data.streak;
            } else { alert(data.msg); }
        }

        async function handleCheckinClick() {
            count++;
            clearTimeout(timer);
            if (count >= 10) {
                count = 0;
                document.getElementById("admin-modal").style.display = "flex";
                return;
            }
            timer = setTimeout(() => { count = 0; }, 3000);

            const res = await fetch('/api/checkin', {method: 'POST'});
            const data = await res.json();
            alert(data.msg);
            if(data.success) document.getElementById("streak-display").innerText = data.streak;
        }

        async function submitAdminLogin() {
            const u = document.getElementById("admin-user").value;
            const p = document.getElementById("admin-pass").value;
            const res = await fetch('/admin-login', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({username: u, password: p})});
            const data = await res.json();
            if (data.success) { window.location.href = '/admin'; } else { alert(data.msg); }
        }

        const socket = io();
        const chatBox = document.getElementById("chat-box");
        socket.on('load_history', (msgs) => { chatBox.innerHTML = ""; msgs.forEach(m => appendMsg(m)); });
        socket.on('receive_message', (m) => { appendMsg(m); });

        function sendMsg() {
            const input = document.getElementById("msg-input");
            if(input.value.trim() !== "") { socket.emit('send_message', {message: input.value}); input.value = ""; }
        }
        document.getElementById("msg-input").addEventListener("keypress", (e) => { if(e.key === "Enter") sendMsg(); });

        function appendMsg(m) {
            const div = document.createElement("div");
            div.className = "msg";
            div.innerHTML = `<b>[${m.time}] ${m.user}:</b> ${m.text}`;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        let playing = true;
        function toggleYtMusic() {
            const iframe = document.getElementById("youtube-audio");
            const btn = document.getElementById("music-btn");
            if(playing) { iframe.src = ""; btn.innerText = "🔇 Bật nhạc"; playing = false; }
            else { iframe.src = "https://www.youtube.com/embed/n8l_j0UKT3Y?autoplay=1&loop=1&playlist=n8l_j0UKT3Y"; btn.innerText = "🎵 Nhạc Tết"; playing = true; }
        }
    </script>
</body>
</html>
'''

ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Admin - Dũng Đẹp Trai</title>
    <style>
        body { font-family: sans-serif; padding: 20px; background: #1a1a2e; color: #fff; }
        table { width: 100%; border-collapse: collapse; background: #16213e; margin-top: 15px; border-radius: 6px; overflow: hidden; }
        th, td { border: 1px solid #1f4068; padding: 10px; text-align: left; font-size: 14px; }
        th { background: #e94560; color: white; }
        .card { background: #16213e; padding: 15px; border-radius: 8px; border: 1px solid #e94560; }
        a { color: #f8b500; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>📊 Bảng Quản Trị Hệ Thống - Admin Dũng</h2>
        <p>Tin nhắn: <b>{{ msg_count }} / 1000</b></p>
        <p><a href="/">⬅ Về trang chủ</a></p>
    </div>
    <h3>Danh sách người dùng</h3>
    <table>
        <tr><th>Tài khoản</th><th>Streak</th><th>Điểm danh gần nhất</th></tr>
        {% for user, data in users.items() %}
        <tr>
            <td><b>{{ user }}</b></td>
            <td>{{ data.streak }} ngày 🔥</td>
            <td>{{ data.last_checkin or 'Chưa' }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
'''

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
