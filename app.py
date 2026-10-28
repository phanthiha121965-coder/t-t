from flask import Flask, render_template_string, request, jsonify, session
from flask_socketio import SocketIO, emit
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tet_dinh_mui_2027_dungdepzai_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- DATABASE TẠM TRÊN RAM ---
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
        return jsonify({"success": False, "msg": "Sai mật khẩu rồi, nhập lại xem nào!"})
    
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
        return jsonify({"success": False, "msg": "Hôm nay ông điểm danh rồi, mai vào lại nhé!"})
    
    udata["streak"] += 1
    udata["last_checkin"] = today
    return jsonify({"success": True, "msg": f"Điểm danh thành công! Chuỗi Streak: {udata['streak']} ngày 🔥", "streak": udata['streak']})

# --- ĐĂNG NHẬP ADMIN BẰNG TÀI KHOẢN YÊU CẦU ---
@app.route('/admin-login', methods=['POST'])
def admin_login():
    data = request.json
    if data.get('username') == ADMIN_USER and data.get('password') == ADMIN_PASS:
        session['is_admin'] = True
        return jsonify({"success": True})
    return jsonify({"success": False, "msg": "Sai tài khoản hoặc mật khẩu Admin rồi!"})

@app.route('/admin', methods=['GET'])
def admin():
    if not session.get('is_admin'):
        return "<h3>Truy cập bị từ chối! Hãy bấm 10 lần vào nút điểm danh ngoài trang chủ để đăng nhập.</h3>", 403
    return render_template_string(ADMIN_TEMPLATE, users=users_db, msg_count=len(messages_db))

# --- REALTIME CHAT (TỰ ĐỘNG XÓA 500 TIN KHI ĐẠT 1000) ---
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


# --- GIAO DIỆN SIÊU ĐẸP CHỦ ĐỀ TẾT (GLASSMORPHISM + HOA MAI ĐỎ VÀNG) ---
FULL_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đếm Ngược Tết 2027 - Dũng Đẹp Trai</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        :root {
            --bg-tet: linear-gradient(135deg, #2b0909 0%, #1a0202 50%, #0f0101 100%);
            --card-bg: rgba(26, 33, 62, 0.75);
            --border-tet: rgba(248, 181, 0, 0.3);
            --gold: #f8b500;
            --red-tet: #e94560;
        }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: var(--bg-tet); 
            background-attachment: fixed;
            color: #fff; 
            text-align: center; 
            margin: 0; 
            padding: 15px; 
            overflow-x: hidden;
        }
        
        /* HIỆU ỨNG TẾT: HOA MAI RƠI / ĐÈN LỒNG */
        .tet-header {
            background: linear-gradient(90deg, #ff2a2a, #ff9900, #ff2a2a);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 22px;
            font-weight: 900;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
            text-shadow: 0 0 20px rgba(255,42,42,0.5);
        }
        
        .badge-brand {
            display: inline-block;
            background: linear-gradient(135deg, #f8b500, #ff6b81);
            color: #1a0202;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 12px;
            margin-bottom: 12px;
            box-shadow: 0 0 10px rgba(248,181,0,0.5);
        }

        .box { 
            background: var(--card-bg); 
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-radius: 16px; 
            padding: 20px; 
            margin: 15px auto; 
            max-width: 450px; 
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5); 
            border: 1px solid var(--border-tet); 
        }

        #timer { 
            font-size: 20px; 
            font-weight: bold; 
            color: var(--gold); 
            margin: 10px 0; 
            background: rgba(0,0,0,0.3);
            padding: 10px;
            border-radius: 10px;
            border: 1px dashed var(--gold);
        }

        input { 
            background: rgba(15, 52, 96, 0.8); 
            color: #fff; 
            border: 1px solid var(--red-tet); 
            width: calc(100% - 24px); 
            max-width: 320px; 
            padding: 12px;
            margin: 6px 0;
            border-radius: 8px;
            outline: none;
            font-size: 14px;
        }
        input:focus { border-color: var(--gold); box-shadow: 0 0 8px rgba(248,181,0,0.4); }

        button { 
            background: linear-gradient(135deg, #e94560, #ff6b81); 
            color: white; 
            cursor: pointer; 
            font-weight: bold; 
            padding: 12px 20px;
            margin: 6px 0;
            border-radius: 8px;
            border: none;
            font-size: 14px;
            transition: 0.3s;
            box-shadow: 0 4px 15px rgba(233,69,96,0.4);
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        button:hover { transform: translateY(-2px); filter: brightness(1.1); }

        #chat-box { 
            height: 220px; 
            overflow-y: scroll; 
            background: rgba(10, 25, 47, 0.9); 
            text-align: left; 
            padding: 12px; 
            border-radius: 10px; 
            margin-bottom: 12px; 
            border: 1px solid rgba(233,69,96,0.3); 
        }
        .msg { margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 6px; font-size: 13px; word-break: break-word; }
        .msg b { color: var(--gold); }

        /* NÚT NHẠC NỔI GÓC MÀN HÌNH */
        #music-btn { 
            position: fixed; bottom: 20px; right: 20px; z-index: 999; 
            background: linear-gradient(135deg, #f8b500, #ff6b81); 
            color: #1a0202; border: none; padding: 12px 18px; border-radius: 50px; 
            cursor: pointer; font-weight: bold; box-shadow: 0 4px 20px rgba(248,181,0,0.5); 
            display: flex; align-items: center; gap: 8px; font-size: 13px;
        }
        
        .wave-bar { display: inline-block; width: 3px; height: 12px; background: #1a0202; animation: wave 0.8s infinite ease-in-out; }
        .wave-bar:nth-child(2) { animation-delay: 0.2s; height: 18px; }
        .wave-bar:nth-child(3) { animation-delay: 0.4s; height: 8px; }
        @keyframes wave { 0%, 100% { transform: scaleY(0.4); } 50% { transform: scaleY(1); } }

        /* MODAL ĐĂNG NHẬP ADMIN BÍ MẬT */
        #admin-modal {
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8); z-index: 9999; justify-content: center; align-items: center;
        }
        .modal-content {
            background: #16213e; padding: 25px; border-radius: 16px; border: 2px solid var(--gold);
            width: 90%; max-width: 350px; text-align: center; box-shadow: 0 0 30px rgba(248,181,0,0.4);
        }
    </style>
</head>
<body>

    <div class="tet-header">🧨 ĐẾM NGƯỢC TẾT ĐÌNH MÙI 2027 🧨</div>
    <div class="badge-brand">👑 THƯƠNG HIỆU ĐỘC QUYỀN: DŨNG ĐẸP TRAI 👑</div>
    <div id="timer">Đang tải thời gian...</div>

    <!-- KHU VỰC ĐĂNG NHẬP / ĐIỂM DANH -->
    <div class="box">
        <div id="auth-section">
            <h3 style="color:var(--gold)">🔑 Đăng ký / Đăng nhập</h3>
            <input type="text" id="username" placeholder="Tên tài khoản của ông"><br>
            <input type="password" id="password" placeholder="Mật khẩu"><br>
            <button onclick="login()">Vào Web Ngay</button>
        </div>
        <div id="user-section" style="display:none;">
            <h2 style="margin:5px 0;">Chào ông, <span id="user-display" style="color:var(--gold);"></span>! 😎</h2>
            <p style="margin:8px 0;">🔥 Chuỗi điểm danh: <b id="streak-display" style="color:var(--red-tet); font-size:20px;">0</b> ngày</p>
            <!-- NÚT ĐIỂM DANH: ẤM 10 LẦN ĐỂ MỞ ADMIN -->
            <button id="checkin-btn" onclick="handleCheckinClick()">Điểm Danh Hôm Nay</button>
        </div>
    </div>

    <!-- KHU VỰC CHAT REALTIME -->
    <div class="box">
        <h3 style="color:var(--gold); margin-top:0;">💬 Khung Chat Cộng Đồng</h3>
        <div id="chat-box"></div>
        <div style="display: flex; gap: 5px;">
            <input type="text" id="msg-input" placeholder="Nhập tin nhắn..." style="flex: 1; margin:0;">
            <button onclick="sendMsg()" style="margin:0; padding: 0 15px;">Gửi</button>
        </div>
    </div>

    <!-- MODAL ĐĂNG NHẬP ADMIN BÍ MẬT -->
    <div id="admin-modal">
        <div class="modal-content">
            <h3 style="color:var(--red-tet)">🔒 Đăng Nhập Cấm Địa Admin</h3>
            <input type="text" id="admin-user" placeholder="Tài khoản Admin"><br>
            <input type="password" id="admin-pass" placeholder="Mật khẩu Admin"><br><br>
            <button onclick="submitAdminLogin()" style="width:100%">Đăng Nhập Quản Trị</button>
            <button onclick="closeAdminModal()" style="background:#555; width:100%; margin-top:5px;">Đóng</button>
        </div>
    </div>

    <!-- KHUNG NHẠC YOUTUBE -->
    <iframe id="youtube-audio" width="0" height="0" src="https://www.youtube.com/embed/n8l_j0UKT3Y?autoplay=1&loop=1&playlist=n8l_j0UKT3Y" frameborder="0" allow="autoplay"></iframe>
    
    <button onclick="toggleYtMusic()" id="music-btn">
        <span id="music-icon" style="display:flex; align-items:center; gap:2px;">
            <span class="wave-bar"></span><span class="wave-bar"></span><span class="wave-bar"></span>
        </span>
        <span id="music-text">Nhạc Tết 2027</span>
    </button>

    <script>
        // --- 1. ĐẾM NGƯỢC TẾT 2027 ---
        const tetDate = new Date("Jan 29, 2027 00:00:00").getTime();
        setInterval(() => {
            const now = new Date().getTime();
            const distance = tetDate - now;
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);
            document.getElementById("timer").innerHTML = `${days} Ngày ${hours} Giờ ${minutes} Phút ${seconds} Giây`;
        }, 1000);

        // --- 2. LOGIN & CHECK-IN & BÍ MẬT 10 LẦN MỞ ADMIN ---
        let checkinClickCount = 0;
        let clickTimer = null;

        async function login() {
            const u = document.getElementById("username").value;
            const p = document.getElementById("password").value;
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u, password: p})
            });
            const data = await res.json();
            if (data.success) {
                document.getElementById("auth-section").style.display = "none";
                document.getElementById("user-section").style.display = "block";
                document.getElementById("user-display").innerText = data.username;
                document.getElementById("streak-display").innerText = data.user_data.streak;
            } else {
                alert(data.msg);
            }
        }

        async function handleCheckinClick() {
            // Đếm số lần bấm liên tục trong vòng 3 giây để mở Admin
            checkinClickCount++;
            clearTimeout(clickTimer);
            
            if (checkinClickCount >= 10) {
                checkinClickCount = 0;
                document.getElementById("admin-modal").style.display = "flex";
                return;
            }
            
            clickTimer = setTimeout(() => {
                checkinClickCount = 0;
            }, 3000);

            // Gọi hàm điểm danh thực tế
            const res = await fetch('/api/checkin', {method: 'POST'});
            const data = await res.json();
            alert(data.msg);
            if(data.success) document.getElementById("streak-display").innerText = data.streak;
        }

        function closeAdminModal() {
            document.getElementById("admin-modal").style.display = "none";
        }

        async function submitAdminLogin() {
            const u = document.getElementById("admin-user").value;
            const p = document.getElementById("admin-pass").value;
            const res = await fetch('/admin-login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u, password: p})
            });
            const data = await res.json();
            if (data.success) {
                window.location.href = '/admin';
            } else {
                alert(data.msg);
            }
        }

        // --- 3. CHAT REALTIME ---
        const socket = io();
        const chatBox = document.getElementById("chat-box");

        socket.on('load_history', (msgs) => {
            chatBox.innerHTML = "";
            msgs.forEach(m => appendMsg(m));
        });

        socket.on('receive_message', (m) => {
            appendMsg(m);
        });

        function sendMsg() {
            const input = document.getElementById("msg-input");
            if(input.value.trim() !== "") {
                socket.emit('send_message', {message: input.value});
                input.value = "";
            }
        }

        document.getElementById("msg-input").addEventListener("keypress", function(event) {
            if (event.key === "Enter") { sendMsg(); }
        });

        function appendMsg(m) {
            const div = document.createElement("div");
            div.className = "msg";
            div.innerHTML = `<b>[${m.time}] ${m.user}:</b> ${m.text}`;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        // --- 4. ĐIỀU KHIỂN NHẠC YOUTUBE ---
        let ytPlaying = true;
        const videoId = "n8l_j0UKT3Y"; 
        const mText = document.getElementById("music-text");
        const mIcon = document.getElementById("music-icon");
        
        function toggleYtMusic() {
            const iframe = document.getElementById("youtube-audio");
            if (ytPlaying) {
                iframe.src = ""; 
                mText.innerHTML = "Tắt nhạc";
                mIcon.innerHTML = '▶';
                ytPlaying = false;
            } else {
                iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&loop=1&playlist=${videoId}`;
                mText.innerHTML = "Nhạc Tết 2027";
                mIcon.innerHTML = '<span class="wave-bar"></span><span class="wave-bar"></span><span class="wave-bar"></span>';
                ytPlaying = true;
            }
        }
    </script>
</body>
</html>
'''

# --- GIAO DIỆN TRANG ADMIN ---
ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Admin - Dũng Đẹp Trai</title>
    <style>
        body { font-family: sans-serif; padding: 20px; background: #1a1a2e; color: #fff; }
        table { width: 100%; border-collapse: collapse; background: #16213e; margin-top: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); border-radius: 8px; overflow: hidden; }
        th, td { border: 1px solid #1f4068; padding: 12px; text-align: left; }
        th { background: #e94560; color: white; }
        .card { background: #16213e; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); border: 1px solid #e94560; }
        a { color: #f8b500; text-decoration: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="card">
        <h2>📊 Bảng Quản Trị Hệ Thống - Admin Dũng</h2>
        <p>Bộ nhớ tin nhắn hiện tại: <b>{{ msg_count }} / 1000 tin</b> (Đạt 1000 tự động xóa 500 tin cũ)</p>
        <p><a href="/">⬅ Quay lại trang chủ</a></p>
    </div>
    
    <h3 style="margin-top:20px;">Danh sách người dùng & Điểm danh</h3>
    <table>
        <tr>
            <th>Tài khoản</th>
            <th>Chuỗi Streak</th>
            <th>Ngày điểm danh gần nhất</th>
        </tr>
        {% for user, data in users.items() %}
        <tr>
            <td><b>{{ user }}</b></td>
            <td>{{ data.streak }} ngày 🔥</td>
            <td>{{ data.last_checkin or 'Chưa điểm danh' }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
'''

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
e-bar"></span><span class="wave-bar"></span><span class="wave-bar"></span>
        </span>
        <span id="music-text">Đang phát Nhạc Tết</span>
    </button>

    <script>
        // --- 1. ĐẾM NGƯỢC TẾT 2027 ---
        const tetDate = new Date("Jan 29, 2027 00:00:00").getTime();
        setInterval(() => {
            const now = new Date().getTime();
            const distance = tetDate - now;
            const days = Math.floor(distance / (1000 * 60 * 60 * 24));
            const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((distance % (1000 * 60)) / 1000);
            document.getElementById("timer").innerHTML = `${days} Ngày ${hours} Giờ ${minutes} Phút ${seconds} Giây`;
        }, 1000);

        // --- 2. LOGIN & CHECK-IN ---
        async function login() {
            const u = document.getElementById("username").value;
            const p = document.getElementById("password").value;
            const res = await fetch('/api/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({username: u, password: p})
            });
            const data = await res.json();
            if (data.success) {
                document.getElementById("auth-section").style.display = "none";
                document.getElementById("user-section").style.display = "block";
                document.getElementById("user-display").innerText = data.username;
                document.getElementById("streak-display").innerText = data.user_data.streak;
            } else {
                alert(data.msg);
            }
        }

        async function checkin() {
            const res = await fetch('/api/checkin', {method: 'POST'});
            const data = await res.json();
            alert(data.msg);
            if(data.success) document.getElementById("streak-display").innerText = data.streak;
        }

        // --- 3. CHAT REALTIME ---
        const socket = io();
        const chatBox = document.getElementById("chat-box");

        socket.on('load_history', (msgs) => {
            chatBox.innerHTML = "";
            msgs.forEach(m => appendMsg(m));
        });

        socket.on('receive_message', (m) => {
            appendMsg(m);
        });

        function sendMsg() {
            const input = document.getElementById("msg-input");
            if(input.value.trim() !== "") {
                socket.emit('send_message', {message: input.value});
                input.value = "";
            }
        }

        document.getElementById("msg-input").addEventListener("keypress", function(event) {
            if (event.key === "Enter") { sendMsg(); }
        });

        function appendMsg(m) {
            const div = document.createElement("div");
            div.className = "msg";
            div.innerHTML = `<b>[${m.time}] ${m.user}:</b> ${m.text}`;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        // --- 4. ĐIỀU KHIỂN NHẠC YOUTUBE ---
        let ytPlaying = true;
        const videoId = "n8l_j0UKT3Y"; 
        const mText = document.getElementById("music-text");
        const mIcon = document.getElementById("music-icon");
        
        function toggleYtMusic() {
            const iframe = document.getElementById("youtube-audio");
            if (ytPlaying) {
                iframe.src = ""; 
                mText.innerHTML = "Đã tắt nhạc";
                mIcon.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="1" y1="1" x2="23" y2="23"></line><path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6"></path><path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line></svg>';
                ytPlaying = false;
            } else {
                iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&loop=1&playlist=${videoId}`;
                mText.innerHTML = "Đang phát Nhạc Tết";
                mIcon.innerHTML = '<span class="wave-bar"></span><span class="wave-bar"></span><span class="wave-bar"></span>';
                ytPlaying = true;
            }
        }
    </script>
</body>
</html>
'''

# --- GIAO DIỆN TRANG ADMIN ---
ADMIN_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Admin - Dũng Đẹp Trai</title>
    <style>
        body { font-family: sans-serif; padding: 20px; background: #f4f4f9; color: #333; }
        table { width: 100%; border-collapse: collapse; background: #fff; margin-top: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
        th { background: #e94560; color: white; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
    </style>
</head>
<body>
    <div class="card">
        <h2>📊 Bảng Quản Trị Hệ Thống - Dũng Đẹp Trai</h2>
        <p>Bộ nhớ tin nhắn hiện tại: <b>{{ msg_count }} / 1000 tin</b> (Đạt 1000 tự động xóa 500 tin cũ)</p>
    </div>
    
    <h3>Danh sách người dùng & Điểm danh</h3>
    <table>
        <tr>
            <th>Tài khoản</th>
            <th>Chuỗi Streak</th>
            <th>Ngày điểm danh gần nhất</th>
        </tr>
        {% for user, data in users.items() %}
        <tr>
            <td><b>{{ user }}</b></td>
            <td>{{ data.streak }} ngày 🔥</td>
            <td>{{ data.last_checkin or 'Chưa điểm danh' }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
'''

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
  
