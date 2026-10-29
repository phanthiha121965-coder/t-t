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

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json or {}
    u = data.get('username', '').strip()
    p = data.get('password', '').strip()
    if not u or not p:
        return jsonify({"success": False, "msg": "Vui lòng nhập đầy đủ thông tin!"})
    if u in users_db:
        return jsonify({"success": False, "msg": "Tài khoản này đã tồn tại, hãy đăng nhập!"})
    users_db[u] = {"password": p, "streak": 0, "last_checkin": None}
    return jsonify({"success": True, "msg": "Đăng ký thành công! Hãy chuyển sang phần Đăng nhập."})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json or {}
    u = data.get('username', '').strip()
    p = data.get('password', '').strip()
    if not u or not p:
        return jsonify({"success": False, "msg": "Vui lòng nhập tài khoản và mật khẩu!"})
    if u not in users_db or users_db[u]["password"] != p:
        return jsonify({"success": False, "msg": "Sai tài khoản hoặc mật khẩu rồi!"})
    session['user'] = u
    return jsonify({"success": True, "username": u, "user_data": users_db[u]})

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
        return "<h3>Truy cập bị từ chối! Bấm 10 lần vào nút điểm danh ngoài trang chủ để mở khóa trang quản trị.</h3>", 403
    sorted_users = sorted(users_db.items(), key=lambda x: x[1]['streak'], reverse=True)
    return render_template_string(ADMIN_HTML, users=sorted_users, msg_count=len(messages_db))

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
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');
        body { 
            font-family: 'Montserrat', sans-serif; 
            background: #000000; color: #fff; text-align: center; margin: 0; padding: 15px 15px 80px 15px; 
            background-image: radial-gradient(circle at center, #1a0808 0%, #000000 100%);
            background-attachment: fixed;
        }
        .card { 
            background: #0a0a0a; border: 1px solid rgba(248,181,0,0.4); border-radius: 20px; 
            padding: 22px; margin: 15px auto; max-width: 400px; box-shadow: 0 0 25px rgba(248,181,0,0.15); 
        }
        .btn { 
            background: linear-gradient(135deg, #f8b500 0%, #d4af37 50%, #aa771c 100%); 
            color: #000; font-weight: 700; padding: 14px 20px; border-radius: 30px; border: none; 
            width: 100%; max-width: 300px; cursor: pointer; margin-top: 10px; font-size: 14px; 
            text-transform: uppercase; box-shadow: 0 4px 15px rgba(248,181,0,0.4); transition: 0.3s;
            white-space: nowrap;
        }
        .btn:hover { transform: scale(1.02); filter: brightness(1.15); }
        .timer { font-size: 16px; font-weight: bold; color: #f8b500; background: rgba(20,20,20,0.9); padding: 12px; border-radius: 14px; border: 1px dashed #d4af37; text-shadow: 0 0 10px rgba(248,181,0,0.3); }
        input { 
            background: #141414; color: #f8b500; border: 1px solid #d4af37; padding: 12px; 
            border-radius: 12px; width: calc(100% - 24px); max-width: 280px; margin: 8px 0; 
            text-align: center; outline: none; font-size: 14px;
        }
        input::placeholder { color: #555; }
        #chat-box { height: 170px; overflow-y: scroll; background: #050505; text-align: left; padding: 12px; border-radius: 12px; border: 1px solid rgba(212,175,55,0.3); margin-bottom: 10px; color: #fff; }
        .msg { font-size: 13px; margin-bottom: 8px; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 6px; word-break: break-word; color: #ddd; }
        .msg b { color: #f8b500; }
        
        #firework-screen {
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #000; z-index: 99999; justify-content: center; align-items: center; flex-direction: column;
            overflow: hidden;
        }
        #giant-number {
            font-size: 90px; font-weight: 900; color: #f8b500;
            text-shadow: 0 0 30px #ff3333, 0 0 60px #f8b500;
            animation: pulseNum 1s infinite alternate;
        }
        @keyframes pulseNum {
            0% { transform: scale(0.9); opacity: 0.8; }
            100% { transform: scale(1.1); opacity: 1; }
        }
        canvas { display: block; position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }

        #modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.9); z-index: 9999; justify-content: center; align-items: center; }
        .modal-content { background: #0a0a0a; padding: 25px; border-radius: 20px; border: 2px solid #f8b500; width: 85%; max-width: 320px; box-shadow: 0 0 30px rgba(248,181,0,0.3); }
        
        #music-btn { position: fixed; bottom: 20px; right: 20px; z-index: 9999; background: linear-gradient(135deg, #f8b500, #d4af37); color: #000; border: none; padding: 12px 20px; border-radius: 30px; font-weight: bold; cursor: pointer; box-shadow: 0 4px 20px rgba(248,181,0,0.6); }
        .switch-link { color: #f8b500; cursor: pointer; font-size: 13px; margin-top: 10px; display: inline-block; text-decoration: underline; }
    </style>
</head>
<body>
    <div style="font-size:32px; margin-top:5px;">🏮</div>
    <h2 style="color:#f8b500; margin:5px 0; letter-spacing:1px;">TẾT ĐINH MÙI 2027</h2>
    <div style="font-size:12px; color:#d4af37; margin-bottom:15px; font-weight:600;">Mùng 1 Tết: 06/02/2027 (Dương Lịch)</div>

    <div class="card">
        <div class="timer" id="timer">Đang tải thời gian...</div>
    </div>

    <div class="card">
        <!-- ĐĂNG NHẬP -->
        <div id="login-box">
            <h3 style="color:#f8b500; margin-top:0;">🔑 Đăng Nhập</h3>
            <input type="text" id="login-u" placeholder="Tên tài khoản"><br>
            <input type="password" id="login-p" placeholder="Mật khẩu"><br>
            <button class="btn" onclick="login()">Đăng Nhập</button>
            <br><span class="switch-link" onclick="showRegister()">Chưa có tài khoản? Đăng ký ngay</span>
        </div>

        <!-- ĐĂNG KÝ -->
        <div id="register-box" style="display:none;">
            <h3 style="color:#f8b500; margin-top:0;">📝 Đăng Ký Tài Khoản</h3>
            <input type="text" id="reg-u" placeholder="Tên tài khoản mới"><br>
            <input type="password" id="reg-p" placeholder="Mật khẩu mới"><br>
            <button class="btn" onclick="register()">Đăng Ký Ngay</button>
            <br><span class="switch-link" onclick="showLogin()">Đã có tài khoản? Đăng nhập</span>
        </div>

        <!-- SAU KHI ĐĂNG NHẬP THÀNH CÔNG -->
        <div id="user-box" style="display:none;">
            <h3 style="color:#f8b500; margin-top:0;">Chào, <span id="uname" style="color:#fff;"></span>! 😎</h3>
            <p style="font-size:15px;">🔥 Streak: <b id="streak" style="color:#ff3333; font-size:18px;">0</b> ngày</p>
            <button class="btn" onclick="checkin()">✨ Điểm Danh Hôm Nay ✨</button>
        </div>
    </div>

    <div class="card">
        <h3 style="color:#f8b500; margin-top:0;">💬 Khung Chat Cộng Đồng</h3>
        <div id="chat-box"></div>
        <div style="display:flex; gap:8px; justify-content:center;">
            <input type="text" id="msg" placeholder="Nhập lời chúc Tết..." style="flex:1; margin:0;">
            <button class="btn" onclick="send()" style="width:auto; padding:12px 18px; margin:0;">Gửi</button>
        </div>
    </div>

    <div id="firework-screen">
        <div id="giant-number">3</div>
        <canvas id="fireworkCanvas"></canvas>
    </div>

    <div id="modal">
        <div class="modal-content">
            <h3 style="color:#f8b500; margin-top:0;">🔒 Đăng Nhập Admin</h3>
            <input type="text" id="au" placeholder="Tài khoản Admin"><br>
            <input type="password" id="ap" placeholder="Mật khẩu Admin"><br><br>
            <button class="btn" onclick="adminLogin()">Xác Nhận</button>
            <button class="btn" onclick="document.getElementById('modal').style.display='none'" style="background:#222; color:#fff; margin-top:8px;">Đóng</button>
        </div>
    </div>

    <div id="player-container"></div>
    <button onclick="toggleMusic()" id="music-btn">🎵 Tắt Nhạc Tết</button>

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
                document.getElementById("timer").innerHTML = `${days} Ngày ${hours} Giờ ${mins} Phút ${secs} Giây`;
            } else {
                startVoiceFireworks();
            }
        }, 1000);

        function speakText(text) {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'vi-VN';
                window.speechSynthesis.speak(utterance);
            }
        }

        function startVoiceFireworks() {
            const screen = document.getElementById("firework-screen");
            const numEl = document.getElementById("giant-number");
            screen.style.display = "flex";
            let count = 3;
            numEl.innerText = count;
            speakText("3");
            const countdownInterval = setInterval(() => {
                count--;
                if (count > 0) { 
                    numEl.innerText = count; 
                    speakText(count.toString());
                } else if (count === 0) { 
                    numEl.innerText = "🎉 CHÚC MỪNG NĂM MỚI 🎉"; 
                    speakText("Chúc mừng năm mới!");
                } else {
                    clearInterval(countdownInterval);
                    numEl.innerText = "";
                    initFireworksCanvas();
                }
            }, 1000);
        }

        function showRegister() {
            document.getElementById('login-box').style.display = 'none';
            document.getElementById('register-box').style.display = 'block';
        }
        function showLogin() {
            document.getElementById('register-box').style.display = 'none';
            document.getElementById('login-box').style.display = 'block';
        }

        async function register() {
            const uVal = document.getElementById('reg-u').value.trim();
            const pVal = document.getElementById('reg-p').value.trim();
            if(!uVal || !pVal) { alert("Vui lòng điền đầy đủ tài khoản và mật khẩu đăng ký!"); return; }
            const res = await fetch('/api/register', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username: uVal, password: pVal})});
            const data = await res.json();
            alert(data.msg);
            if(data.success) { showLogin(); }
        }

        async function login() {
            const uVal = document.getElementById('login-u').value.trim();
            const pVal = document.getElementById('login-p').value.trim();
            if(!uVal || !pVal) { alert("Vui lòng điền đầy đủ tài khoản và mật khẩu đăng nhập!"); return; }
            const res = await fetch('/api/login', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username: uVal, password: pVal})});
            const data = await res.json();
            if(data.success) {
                document.getElementById('login-box').style.display = 'none';
                document.getElementById('register-box').style.display = 'none';
                document.getElementById('user-box').style.display = 'block';
                document.getElementById('uname').innerText = data.username;
                document.getElementById('streak').innerText = data.user_data.streak;
            } else { alert(data.msg); }
        }

        let count = 0, t = null;
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
            const container = document.getElementById('player-container');
            const btn = document.getElementById('music-btn');
            if(play) { container.innerHTML = ''; btn.innerText = '🎵 Bật Nhạc Tết'; play = false; }
            else { container.innerHTML = '<iframe width="0" height="0" src="https://www.youtube.com/embed/n8l_j0UKT3Y?autoplay=1&loop=1&playlist=n8l_j0UKT3Y" frameborder="0" allow="autoplay"></iframe>'; btn.innerText = '🎵 Tắt Nhạc Tết'; play = true; }
        }
    </script>
</body>
</html>"""

ADMIN_HTML = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Admin - Dũng Đẹp Trai</title>
<style>
    body { font-family:sans-serif; background:#000; color:#f8b500; padding:20px; }
    table { width:100%; border-collapse:collapse; background:#0a0a0a; margin-top:15px; border:1px solid #d4af37; border-radius:10px; overflow:hidden; }
    th, td { border:1px solid #333; padding:12px; text-align:left; font-size:14px; }
    th { background:#d4af37; color:#000; font-weight:bold; }
    .card { background:#0a0a0a; padding:20px; border-radius:12px; border:1px solid #d4af37; box-shadow: 0 0 15px rgba(248,181,0,0.2); }
    a { color:#f8b500; font-weight:bold; text-decoration:none; }
    .btn-test { background: #ff3333; color: #fff; padding: 10px 15px; border-radius: 8px; border: none; font-weight: bold; cursor: pointer; text-decoration: none; display: inline-block; margin-top: 10px; }
</style>
</head>
<body>
    <div class="card">
        <h2>📊 Bảng Quản Trị Hệ Thống - Admin Dũng</h2>
        <p>Tổng tin nhắn chat: <b>{{ msg_count }} / 1000</b></p>
        <p><a href="/">⬅ Về trang chủ</a></p>
        <hr style="border-color:#333; margin:15px 0;">
        <h3 style="color:#fff; margin-top:0;">⚡ Khu Vực Thử Nghiệm Pháo Hoa & Giọng Đọc (Chỉ Admin)</h3>
        <p>Bấm nút dưới đây để test trực tiếp hiệu ứng giọng đọc đếm ngược 3 giây và pháo hoa rực rỡ:</p>
        <button class="btn-test" onclick="triggerVoiceFireworks()">🚀 Kích Hoạt Test Giao Thừa Ngay</button>
    </div>

    <h3 style="color:#fff; margin-top:25px;">🏆 Bảng Xếp Hạng Điểm Danh (Streak)</h3>
    <table>
        <tr><th>Hạng 🥇</th><th>Tài khoản</th><th>Chuỗi Streak</th><th>Điểm danh gần nhất</th></tr>
        {% for u, d in users %}
        <tr>
            <td><b>#{{ loop.index }}</b></td>
            <td><b>{{ u }}</b></td>
            <td>{{ d.streak }} ngày 🔥</td>
            <td>{{ d.last_checkin or 'Chưa điểm danh' }}</td>
        </tr>
        {% endfor %}
    </table>

    <div id="firework-screen" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:#000; z-index:99999; justify-content:center; align-items:center; flex-direction:column;">
        <div id="giant-number" style="font-size:90px; font-weight:900; color:#f8b500; text-shadow:0 0 30px #ff3333;">3</div>
        <canvas id="fireworkCanvas" style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none;"></canvas>
    </div>

    <script>
        function speakText(text) {
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.lang = 'vi-VN';
                window.speechSynthesis.speak(utterance);
            }
        }

        function triggerVoiceFireworks() {
            const screen = document.getElementById("firework-screen");
            const numEl = document.getElementById("giant-number");
            screen.style.display = "flex";
            let count = 3;
            numEl.innerText = count;
            speakText("3");
            
            const countdownInterval = setInterval(() => {
                count--;
                if (count > 0) { 
                    numEl.innerText = count; 
                    speakText(count.toString());
                } else if (count === 0) { 
                    numEl.innerText = "🎉 CHÚC MỪNG NĂM MỚI 🎉"; 
                    speakText("Chúc mừng năm mới!");
                } else {
                    clearInterval(countdownInterval);
                    numEl.innerText = "";
                    initFireworksCanvas();
                    setTimeout(() => { location.reload(); }, 6000);
                }
            }, 1000);
        }

        function initFireworksCanvas() {
            const canvas = document.getElementById("fireworkCanvas");
            const ctx = canvas.getContext("2d");
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;

            class Firework {
                constructor() {
                    this.x = Math.random() * canvas.width;
                    this.y = canvas.height;
                    this.sx = this.x; this.sy = canvas.height;
                    this.tx = Math.random() * canvas.width;
                    this.ty = Math.random() * (canvas.height / 2);
                    this.angle = Math.atan2(this.ty - this.sy, this.tx - this.sx);
                    this.speed = 4;
                    this.particles = [];
                    this.exploded = false;
                }
                update() {
                    if (!this.exploded) {
                        this.x += Math.cos(this.angle) * this.speed;
                        this.y += Math.sin(this.angle) * this.speed;
                        if (Math.hypot(this.x - this.sx, this.y - this.sy) >= Math.hypot(this.tx - this.sx, this.ty - this.sy)) {
                            this.exploded = true;
                            for (let i = 0; i < 80; i++) { this.particles.push(new Particle(this.tx, this.ty)); }
                        }
                    }
                    this.particles.forEach((p, index) => {
                        p.update();
                        if (p.alpha <= 0) this.particles.splice(index, 1);
                    });
                }
                draw() {
                    if (!this.exploded) {
                        ctx.fillStyle = "#f8b500";
                        ctx.fillRect(this.x, this.y, 3, 3);
                    }
                    this.particles.forEach(p => p.draw());
                }
            }

            class Particle {
                constructor(x, y) {
                    this.x = x; this.y = y;
                    const angle = Math.random() * Math.PI * 2;
                    const speed = Math.random() * 6;
                    this.vx = Math.cos(angle) * speed;
                    this.vy = Math.sin(angle) * speed;
                    this.alpha = 1;
                    this.decay = Math.random() * 0.015 + 0.010;
                    this.color = `hsl(${Math.random() * 360}, 100%, 60%)`;
                }
                update() {
                    this.x += this.vx; this.y += this.vy;
                    this.vy += 0.05; this.alpha -= this.decay;
                }
                draw() {
                    ctx.save();
                    ctx.globalAlpha = this.alpha;
                    ctx.fillStyle = this.color;
                    ctx.beginPath();
                    ctx.arc(this.x, this.y, 2.5, 0, Math.PI * 2);
                    ctx.fill();
                    ctx.restore();
                }
            }

            let fireworks = [];
            function loop() {
                ctx.fillStyle = "rgba(0, 0, 0, 0.2)";
                ctx.fillRect(0, 0, canvas.width, canvas.height);
                if (Math.random() < 0.08) fireworks.push(new Firework());
                fireworks.forEach((fw, index) => {
                    fw.update(); fw.draw();
                    if (fw.exploded && fw.particles.length === 0) fireworks.splice(index, 1);
                });
                requestAnimationFrame(loop);
            }
            loop();
        }
    </script>
</body>
</html>"""

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
