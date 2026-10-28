from flask import Flask, render_template_string, request, jsonify, session
from flask_socketio import SocketIO, emit
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'tet_dinh_mui_2027_dungdepzai_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# --- DATABASE TẠM TRÊN RAM ---
users_db = {}       # Lưu thông tin user, mật khẩu, streak điểm danh
messages_db = []    # Khung chứa tối đa 1000 tin nhắn chat
ADMIN_PASS = "admin123" # Mật khẩu vào trang quản trị của ông

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

# --- TRANG ADMIN QUẢN LÝ ---
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('admin_pass') == ADMIN_PASS:
            session['is_admin'] = True
    
    if not session.get('is_admin'):
        return '''
            <div style="background:#1a1a2e; color:#fff; height:100vh; display:flex; justify-content:center; align-items:center; font-family:sans-serif;">
                <form method="post" style="background:#16213e; padding:30px; border-radius:12px; text-align:center; box-shadow:0 4px 15px rgba(0,0,0,0.5); border: 1px solid #e94560;">
                    <h2>🔒 Khu Vực Cấm Địa - Admin Dũng</h2>
                    <input type="password" name="admin_pass" placeholder="Nhập mật khẩu Admin" style="padding:10px; border-radius:6px; border:1px solid #e94560; background:#0f3460; color:#fff; margin-right:5px;" required>
                    <button type="submit" style="padding:10px 15px; background:#e94560; color:#fff; border:none; border-radius:6px; cursor:pointer; font-weight:bold;">Vào</button>
                </form>
            </div>
        '''
    
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


# --- GIAO DIỆN CHÍNH (HTML + CSS + SVG ICON TỰ VẼ) ---
FULL_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Đếm Ngược Tết 2027 - Dũng Đẹp Trai</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a2e; color: #fff; text-align: center; margin: 0; padding: 15px; }
        .box { background: #16213e; border-radius: 12px; padding: 20px; margin: 15px auto; max-width: 450px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); border: 1px solid #1f4068; }
        h1 { color: #e94560; font-size: 20px; display: flex; align-items: center; justify-content: center; gap: 8px; }
        #timer { font-size: 22px; font-weight: bold; color: #f8b500; margin: 10px 0; text-shadow: 0 0 10px rgba(248,181,0,0.3); }
        input, button { padding: 10px; margin: 5px; border-radius: 6px; border: none; font-size: 14px; }
        input { background: #0f3460; color: #fff; border: 1px solid #e94560; width: calc(100% - 24px); max-width: 300px; outline: none; }
        button { background: #e94560; color: white; cursor: pointer; font-weight: bold; transition: 0.2s; display: inline-flex; align-items: center; justify-content: center; gap: 6px; }
        button:hover { background: #ff6b81; transform: translateY(-1px); }
        #chat-box { height: 200px; overflow-y: scroll; background: #0f3460; text-align: left; padding: 10px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #1f4068; }
        .msg { margin-bottom: 8px; border-bottom: 1px solid #16213e; padding-bottom: 4px; font-size: 14px; word-break: break-word; }
        .msg b { color: #f8b500; }
        
        /* NÚT NHẠC NỔI GÓC MÀN HÌNH VỚI ICON VECTOR */
        #music-btn { 
            position: fixed; bottom: 20px; right: 20px; z-index: 999; 
            background: linear-gradient(135deg, #e94560, #ff6b81); 
            color: white; border: none; padding: 12px 20px; border-radius: 50px; 
            cursor: pointer; font-weight: bold; box-shadow: 0 4px 20px rgba(233,69,96,0.5); 
            display: flex; align-items: center; gap: 8px; font-size: 14px;
        }
        
        /* HIỆU ỨNG SÓNG NHẠC NHẢY MÚA KHI PHÁT */
        .wave-bar { display: inline-block; width: 3px; height: 12px; background: #fff; animation: wave 0.8s infinite ease-in-out; }
        .wave-bar:nth-child(2) { animation-delay: 0.2s; height: 18px; }
        .wave-bar:nth-child(3) { animation-delay: 0.4s; height: 8px; }
        @keyframes wave { 0%, 100% { transform: scaleY(0.4); } 50% { transform: scaleY(1); } }
    </style>
</head>
<body>

    <!-- TIÊU ĐỀ KÈM ICON PHÁO HOA TỰ VẼ (SVG) -->
    <h1>
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e94560" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/></svg>
        ĐẾM NGƯỢC TẾT ĐÌNH MÙI 2027
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#e94560" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"/></svg>
    </h1>
    <div style="color: #f8b500; font-weight: bold; margin-bottom: 5px; font-size: 14px;">👑 THƯƠNG HIỆU ĐỘC QUYỀN: DŨNG ĐẸP TRAI 👑</div>
    <div id="timer">Đang tính thời gian...</div>

    <!-- KHU VỰC ĐĂNG NHẬP / ĐIỂM DANH -->
    <div class="box">
        <div id="auth-section">
            <h3>🔑 Đăng ký / Đăng nhập</h3>
            <input type="text" id="username" placeholder="Tên tài khoản của ông"><br>
            <input type="password" id="password" placeholder="Mật khẩu"><br>
            <button onclick="login()">
                <!-- Icon Khóa Mở -->
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                Vào Web Ngay
            </button>
        </div>
        <div id="user-section" style="display:none;">
            <h2>Chào ông, <span id="user-display" style="color:#f8b500;"></span>! 😎</h2>
            <p>🔥 Chuỗi điểm danh: <b id="streak-display" style="color:#e94560; font-size:18px;">0</b> ngày</p>
            <button onclick="checkin()">
                <!-- Icon Ngọn Lửa Checkin -->
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.5 4 6.5 2 2 3 4 3 6.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"></path></svg>
                Điểm Danh Hôm Nay
            </button>
        </div>
    </div>

    <!-- KHU VỰC CHAT REALTIME -->
    <div class="box">
        <h3>💬 Khung Chat Cộng Đồng</h3>
        <div id="chat-box"></div>
        <input type="text" id="msg-input" placeholder="Nhập tin nhắn..." style="width: 60%; display: inline-block;">
        <button onclick="sendMsg()" style="width: 28%; display: inline-block;">
            <!-- Icon Máy Bay Gửi Tin Nhắn -->
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            Gửi
        </button>
    </div>

    <!-- KHUNG NHẠC YOUTUBE XUYÊN TẾT (BÀI 7 TIẾNG) -->
    <iframe id="youtube-audio" width="0" height="0" src="https://www.youtube.com/embed/n8l_j0UKT3Y?autoplay=1&loop=1&playlist=n8l_j0UKT3Y" frameborder="0" allow="autoplay"></iframe>
    
    <!-- NÚT NHẠC VỚI SÓNG NHẠC VECTOR ĐỘC QUYỀN -->
    <button onclick="toggleYtMusic()" id="music-btn">
        <span id="music-icon" style="display:flex; align-items:center; gap:2px;">
            <span class="wave-bar"></span><span class="wave-bar"></span><span class="wave-bar"></span>
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
  
