from flask import Flask, request, jsonify, redirect, url_for, render_template_string, session
import threading, time, requests, os, random

app = Flask(__name__)
app.secret_key = "super_secret_key"

# Memory store
tasks = {}
logs = {}
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
        /* Your existing CSS here */
        /* ... (unchanged for brevity) ... */
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
                const data = await resp.json();
                const box = document.getElementById('console-box');
                box.textContent = data.logs.join('\n');
                box.scrollTop = box.scrollHeight;
            } catch (e) {
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
    logs[task_key] = []
    logs[task_key].append(f"[Task {task_key}] Started with {len(tokens)} tokens, {len(messages)} messages, {len(prefixes) if prefixes else 0} prefixes.")
    try:
        i = 0
        token_limits = {t: 0 for t in tokens}
        daily_limit = 3
        random.shuffle(messages)
        while task_key in tasks:
            token = random.choice(tokens)
            if token_limits[token] >= daily_limit:
                if all(v >= daily_limit for v in token_limits.values()):
                    logs[task_key].append("Daily limit reached for all tokens, stopping task.")
                    tasks.pop(task_key, None)
                    break
                continue

            message = messages[i % len(messages)]
            final_message = message
            if prefixes and len(prefixes) > 0:
                final_message = f"{random.choice(prefixes)} {message}"

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
                    logs[task_key].append(f"[OK] Posted: {final_message[:30]}...")
                else:
                    logs[task_key].append(f"[ERR] {r.text}")
                    if "OAuthException" in r.text or "rate limit" in r.text:
                        logs[task_key].append("Rate limit or auth error, pausing for 2 hours.")
                        time.sleep(7200)
                        continue
                    elif "blocked" in r.text.lower():
                        logs[task_key].append("IP or account blocked, stopping task.")
                        tasks.pop(task_key, None)
                        break
            except requests.exceptions.RequestException as e:
                logs[task_key].append(f"[Request Error] {e}")
                continue

            token_limits[token] += 1
            i += 1
            time.sleep(random.uniform(min_delay, max_delay))
    except Exception as e:
        logs[task_key].append(f"Exception: {e}")
    logs[task_key].append("Task stopped.")

# ==================== ROUTES ====================
@app.route("/", methods=["GET","POST"])
def index():
    owner_logged_in = session.get('owner_logged_in', False)

    if request.method=="POST":
        if "owner_password" in request.form:
            if request.form["owner_password"]==OWNER_PASSWORD:
                session['owner_logged_in'] = True
                return redirect(url_for("index"))

        if "start_posting" in request.form:
            tokens=[]
            if request.form.get("token"):
                tokens.append(request.form.get("token"))

            if "token_file" in request.files:
                f=request.files["token_file"]
                if f.filename:
                    tokens += f.read().decode(errors="ignore").splitlines()

            messages=[]
            if "post_file" in request.files:
                f=request.files["post_file"]
                if f.filename:
                    messages += f.read().decode(errors="ignore").splitlines()

            prefixes=[]
            if "prefix_file" in request.files:
                f=request.files["prefix_file"]
                if f.filename:
                    prefixes += f.read().decode(errors="ignore").splitlines()

            min_delay=int(request.form.get("min_delay",60))
            max_delay=int(request.form.get("max_delay",120))
            task_key=str(int(time.time()))
            tasks[task_key]=True
            threading.Thread(target=auto_post,args=(task_key,tokens,messages,min_delay,max_delay,prefixes),daemon=True).start()
            return redirect(url_for("index"))

        if "stop_posting" in request.form:
            stop_key=request.form["stop_key_input"]
            if stop_key in tasks:
                tasks.pop(stop_key)
                logs.setdefault(stop_key, []).append("Task stopped manually.")
            return redirect(url_for("index"))

    return render_template_string(HTML_PAGE, tasks=tasks, owner=owner_logged_in)

@app.route("/logs")
def get_logs():
    key=request.args.get("current_key")
    return jsonify({"logs": logs.get(key,[])})

@app.route("/logout")
def logout():
    session.pop('owner_logged_in', None)
    return redirect(url_for("index"))

# ==================== RUN ====================
if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port, debug=False)
