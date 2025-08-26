from flask import Flask, request, jsonify, redirect, url_for, render_template_string, session
import threading, time, requests, os, random
from threading import Lock

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Memory store with thread lock
tasks = {}
logs = {}
log_lock = Lock()
OWNER_PASSWORD = "vampireayansh"

# 10 User-Agents for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:129.0) Gecko/20100101 Firefox/129.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/128.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
]

# ==================== HTML ====================
HTML_PAGE = """ 
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Facebook Multi-Token Auto Poster</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700&family=Rajdhani:wght@400;500;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-dark: #0d0d12;
            --bg-darker: #07070a;
            --accent: #ff2a6d;
            --accent-dark: #d1004d;
            --text: #e0e0e8;
            --text-dim: #a0a0b0;
            --card-bg: #151520;
            --card-border: #252535;
            --input-bg: #1a1a2a;
        }
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            background-color: var(--bg-dark);
            background-image:
                radial-gradient(circle at 15% 50%, rgba(120, 20, 80, 0.2) 0%, transparent 25%),
                radial-gradient(circle at 85% 30%, rgba(80, 20, 120, 0.2) 0%, transparent 25%),
                radial-gradient(circle at 50% 80%, rgba(160, 30, 90, 0.2) 0%, transparent 25%);
            color: var(--text);
            font-family: 'Rajdhani', sans-serif;
            margin: 0;
            padding: 20px;
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .container {
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            position: relative;
        }
        .header h1 {
            color: var(--accent);
            margin: 0;
            font-size: 3rem;
            letter-spacing: 3px;
            font-family: 'Orbitron', sans-serif;
            font-weight: 700;
            text-transform: uppercase;
            text-shadow: 0 0 15px var(--accent);
            position: relative;
            display: inline-block;
            padding: 0 20px;
        }
        .header h1::before,
        .header h1::after {
            content: '';
            position: absolute;
            top: 50%;
            width: 30px;
            height: 3px;
            background: var(--accent);
            box-shadow: 0 0 10px var(--accent);
        }
        .header h1::before { left: -40px; }
        .header h1::after { right: -40px; }
        .header p {
            color: var(--text-dim);
            margin: 10px 0 0;
            font-size: 1.2rem;
            letter-spacing: 2px;
            font-weight: 500;
        }
        .panel {
            background-color: rgba(21, 21, 32, 0.9);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 0 30px rgba(255, 42, 109, 0.15);
            backdrop-filter: blur(5px);
            position: relative;
            overflow: hidden;
        }
        .panel::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(to right, transparent, var(--accent), transparent);
            box-shadow: 0 0 15px var(--accent);
        }
        .panel-title {
            color: var(--accent);
            margin-top: 0;
            margin-bottom: 25px;
            padding-bottom: 15px;
            font-size: 1.8rem;
            text-shadow: 0 0 5px var(--accent);
            font-family: 'Orbitron', sans-serif;
            letter-spacing: 1px;
            text-align: center;
            border-bottom: 1px solid var(--card-border);
            position: relative;
        }
        .panel-title::after {
            content: '';
            position: absolute;
            bottom: -2px;
            left: 50%;
            transform: translateX(-50%);
            width: 100px;
            height: 3px;
            background: var(--accent);
            box-shadow: 0 0 10px var(--accent);
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            margin-bottom: 10px;
            color: var(--text-dim);
            font-weight: 600;
            font-size: 1.1rem;
            letter-spacing: 0.5px;
        }
        input[type="text"],
        input[type="number"],
        input[type="file"],
        input[type="password"],
        select,
        textarea {
            width: 100%;
            padding: 14px 16px;
            background-color: var(--input-bg);
            border: 1px solid var(--card-border);
            color: var(--text);
            font-family: 'Rajdhani', sans-serif;
            font-size: 1.1rem;
            font-weight: 500;
            border-radius: 6px;
            transition: all 0.3s;
        }
        input:focus,
        textarea:focus {
            outline: none;
            border-color: var(--accent);
            box-shadow: 0 0 10px rgba(255, 42, 109, 0.3);
        }
        button, input[type="submit"] {
            background: linear-gradient(135deg, var(--accent), var(--accent-dark));
            color: white;
            border: none;
            padding: 16px 24px;
            font-family: 'Orbitron', sans-serif;
            font-weight: bold;
            font-size: 1.2rem;
            cursor: pointer;
            width: 100%;
            transition: all 0.3s;
            border-radius: 6px;
            text-transform: uppercase;
            letter-spacing: 2px;
            box-shadow: 0 0 20px rgba(255, 42, 109, 0.3);
            margin-bottom: 15px;
            position: relative;
            overflow: hidden;
            z-index: 1;
        }
        button::before, input[type="submit"]::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: all 0.5s;
            z-index: -1;
        }
        button:hover, input[type="submit"]:hover {
            transform: translateY(-3px);
            box-shadow: 0 0 25px rgba(255, 42, 109, 0.5);
        }
        button:hover::before, input[type="submit"]:hover::before {
            left: 100%;
        }
        .threads-btn {
            background: linear-gradient(135deg, #252540, #151530);
        }
        .threads-btn:hover {
            background: linear-gradient(135deg, #353550, #252540);
        }
        .glow {
            animation: glow 2s infinite alternate;
        }
        @keyframes glow {
            from { text-shadow: 0 0 5px var(--accent); }
            to { text-shadow: 0 0 15px var(--accent), 0 0 25px var(--accent-dark); }
        }
        .file-input-container {
            position: relative;
        }
        .file-input-container::after {
            content: 'Choose File';
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
            background: var(--accent);
            color: white;
            padding: 8px 15px;
            border-radius: 4px;
            font-size: 0.9rem;
            font-weight: 600;
            pointer-events: none;
        }
        input[type="file"] {
            padding-right: 100px;
        }
        #console-box {
            background-color: var(--input-bg);
            border: 1px solid var(--card-border);
            border-radius: 6px;
            padding: 15px;
            color: var(--text);
            font-family: 'Rajdhani', sans-serif;
            font-size: 1rem;
            max-height: 200px;
            overflow-y: auto;
            margin-top: 20px;
            white-space: pre-wrap;
        }
        @media (max-width: 768px) {
            .header h1 { font-size: 2.2rem; }
            .header h1::before, .header h1::after { display: none; }
            .panel { padding: 20px; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 class="glow">OWNER AYANSH PANDIT</h1>
            <p>Facebook Multi-Token Auto Poster</p>
        </div>

        {% if not owner %}
        <div class="panel">
            <h2 class="panel-title">Owner Login</h2>
            <form method="post" action="/">
                <div class="form-group">
                    <label>Enter Owner Password:</label>
                    <input type="password" name="owner_password" required placeholder="Enter password">
                </div>
                <input type="submit" value="Enter">
            </form>
        </div>
        {% endif %}

        {% if owner %}
        <div class="panel">
            <h2 class="panel-title">AYANSH VAMPIRE PANEL 🩷</h2>
            <p>Active tasks: {{ tasks|length }}</p>
            <form method="get" action="/logout">
                <input type="submit" value="Logout" class="threads-btn">
            </form>
        </div>
        {% endif %}

        <div class="panel">
            <h2 class="panel-title">Auto Poster Controls</h2>
            <form method="post" enctype="multipart/form-data">
                <div class="form-group">
                    <label>Facebook Token (single) or leave empty for file:</label>
                    <input type="text" name="token" placeholder="Enter single token">
                </div>
                <div class="form-group">
                    <label>Upload Token File (.txt, one per line):</label>
                    <div class="file-input-container">
                        <input type="file" name="token_file" accept=".txt">
                    </div>
                </div>
                <div class="form-group">
                    <label>Min Delay between posts (seconds):</label>
                    <input type="number" name="min_delay" value="60" min="1" required placeholder="Enter min delay">
                </div>
                <div class="form-group">
                    <label>Max Delay between posts (seconds):</label>
                    <input type="number" name="max_delay" value="120" min="1" required placeholder="Enter max delay">
                </div>
                <div class="form-group">
                    <label>Upload Prefixes File (.txt, optional):</label>
                    <div class="file-input-container">
                        <input type="file" name="prefix_file" accept=".txt">
                    </div>
                </div>
                <div class="form-group">
                    <label>Upload Messages File (.txt, required):</label>
                    <div class="file-input-container">
                        <input type="file" name="post_file" accept=".txt" required>
                    </div>
                </div>
                <input type="submit" name="start_posting" value="Start Posting">
            </form>
        </div>

        <div class="panel">
            <h2 class="panel-title">Stop Posting</h2>
            <form method="post">
                <div class="form-group">
                    <label>Enter Stop Key:</label>
                    <input type="text" name="stop_key_input" required placeholder="Enter task key">
                </div>
                <input type="submit" name="stop_posting" value="Stop Posting">
            </form>
        </div>

        <div class="panel">
            <h2 class="panel-title">Logs</h2>
            <div class="form-group">
                <select id="task-select" onchange="changeTaskKey()">
                    <option value="" disabled selected>Select Task</option>
                    {% for k in tasks.keys() %}
                    <option value="{{k}}">{{k}}</option>
                    {% endfor %}
                </select>
            </div>
            <div id="console-box">No logs yet...</div>
        </div>
    </div>

    <script>
        let currentTaskKey = '';
        function changeTaskKey() {
            const sel = document.getElementById('task-select');
            currentTaskKey = sel.value;
            fetchLogs();
        }
        async function fetchLogs() {
            if (!currentTaskKey) {
                document.getElementById('console-box').textContent = 'No task selected.';
                return;
            }
            try {
                const resp = await fetch('/logs?current_key=' + encodeURIComponent(currentTaskKey));
                if (!resp.ok) throw new Error('Failed to fetch logs');
                const data = await resp.json();
                const box = document.getElementById('console-box');
                box.textContent = data.logs.length > 0 ? data.logs.join('\n') : 'No logs available.';
                box.scrollTop = box.scrollHeight;
            } catch (e) {
                document.getElementById('console-box').textContent = `Error fetching logs: ${e.message}`;
                console.error(e);
            }
        }
        setInterval(fetchLogs, 2000);
    </script>
</body>
</html>
"""

# ==================== AUTO POST FUNCTION ====================
def auto_post(task_key, tokens, messages, min_delay, max_delay, prefixes=None):
    with log_lock:
        logs[task_key] = []
        logs[task_key].append(f"[Task {task_key}] Started at {time.strftime('%H:%M:%S', time.localtime())}")
        logs[task_key].append(f"Debug: Initialized with {len(tokens)} tokens, {len(messages)} messages")
    try:
        i = 0
        token_limits = {t: 0 for t in tokens}
        daily_limit = 3
        if not tokens:
            tokens = ["dummy_token"]  # Default for testing
            with log_lock:
                logs[task_key].append("Warning: No tokens provided, using dummy_token")
        if not messages:
            messages = ["Test message"]  # Default for testing
            with log_lock:
                logs[task_key].append("Warning: No messages provided, using Test message")
        random.shuffle(messages)
        while task_key in tasks:
            token = random.choice(tokens)
            if token_limits[token] >= daily_limit:
                if all(v >= daily_limit for v in token_limits.values()):
                    with log_lock:
                        logs[task_key].append(f"Daily limit reached for all tokens, stopping at {time.strftime('%H:%M:%S', time.localtime())}")
                    tasks.pop(task_key, None)
                    break
                continue

            message = messages[i % len(messages)]
            final_message = message
            if prefixes and len(prefixes) > 0:
                final_message = f"{random.choice(prefixes)} {message}"

            with log_lock:
                logs[task_key].append(f"Debug: Posting with token {token[:5]}... at {time.strftime('%H:%M:%S', time.localtime())}")
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": random.choice(["en-US,en;q=0.5", "en-GB,en;q=0.5", "hi-IN,en;q=0.5"]),
                "Connection": "keep-alive",
                "Referer": random.choice(["https://www.facebook.com/", "https://m.facebook.com/", "https://www.facebook.com/feed"]),
                "Origin": "https://www.facebook.com",
                "DNT": "1"
            }
            url = "https://graph.facebook.com/me/feed"
            params = {"message": final_message, "access_token": token}
            try:
                r = requests.post(url, data=params, headers=headers, timeout=10)
                if r.status_code == 200:
                    with log_lock:
                        logs[task_key].append(f"[OK] Posted: {final_message[:30]}... at {time.strftime('%H:%M:%S', time.localtime())}")
                else:
                    with log_lock:
                        logs[task_key].append(f"[ERR] Status {r.status_code}: {r.text} at {time.strftime('%H:%M:%S', time.localtime())}")
                    if "OAuthException" in r.text or "rate limit" in r.text:
                        with log_lock:
                            logs[task_key].append(f"Rate limit or auth error, pausing for 2 hours at {time.strftime('%H:%M:%S', time.localtime())}")
                        time.sleep(7200)
                        continue
                    elif "blocked" in r.text.lower():
                        with log_lock:
                            logs[task_key].append(f"IP or account blocked, stopping at {time.strftime('%H:%M:%S', time.localtime())}")
                        tasks.pop(task_key, None)
                        break
            except requests.exceptions.RequestException as e:
                with log_lock:
                    logs[task_key].append(f"[Request Error] {e} at {time.strftime('%H:%M:%S', time.localtime())}")
                continue

            token_limits[token] += 1
            i += 1
            time.sleep(random.uniform(min_delay, max_delay))
    except Exception as e:
        with log_lock:
            logs[task_key].append(f"Exception: {e} at {time.strftime('%H:%M:%S', time.localtime())}")
    with log_lock:
        logs[task_key].append(f"Task stopped at {time.strftime('%H:%M:%S', time.localtime())}")

# ==================== ROUTES ====================
@app.route("/", methods=["GET", "POST"])
def index():
    owner_logged_in = session.get('owner_logged_in', False)

    if request.method == "POST":
        if "owner_password" in request.form:
            if request.form["owner_password"] == OWNER_PASSWORD:
                session['owner_logged_in'] = True
                return redirect(url_for("index"))

        if "start_posting" in request.form:
            tokens = []
            if request.form.get("token"):
                tokens.append(request.form.get("token"))

            if "token_file" in request.files:
                f = request.files["token_file"]
                if f.filename:
                    tokens += f.read().decode(errors="ignore").splitlines()

            messages = []
            if "post_file" in request.files:
                f = request.files["post_file"]
                if f.filename:
                    messages += f.read().decode(errors="ignore").splitlines()

            prefixes = []
            if "prefix_file" in request.files:
                f = request.files["prefix_file"]
                if f.filename:
                    prefixes += f.read().decode(errors="ignore").splitlines()

            min_delay = int(request.form.get("min_delay", 60))
            max_delay = int(request.form.get("max_delay", 120))
            task_key = str(int(time.time()))
            tasks[task_key] = True
            threading.Thread(target=auto_post, args=(task_key, tokens, messages, min_delay, max_delay, prefixes), daemon=True).start()
            return redirect(url_for("index"))

        if "stop_posting" in request.form:
            stop_key = request.form["stop_key_input"]
            if stop_key in tasks:
                tasks.pop(stop_key)
                with log_lock:
                    logs.setdefault(stop_key, []).append(f"Task stopped manually at {time.strftime('%H:%M:%S', time.localtime())}")
            return redirect(url_for("index"))

    return render_template_string(HTML_PAGE, tasks=tasks, owner=owner_logged_in)

@app.route("/logs")
def get_logs():
    key = request.args.get("current_key")
    if not key:
        return jsonify({"logs": ["No task key provided"]})
    with log_lock:
        return jsonify({"logs": logs.get(key, ["No logs yet"])})

@app.route("/logout")
def logout():
    session.pop('owner_logged_in', None)
    return redirect(url_for("index"))

# ==================== RUN ====================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
