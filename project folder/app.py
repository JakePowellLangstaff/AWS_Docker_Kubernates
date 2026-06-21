from flask import Flask, request, redirect, render_template_string, jsonify
import sqlite3
import os
import socket

# ===============================================
# APP INITIALIZATION
# ===============================================

app = Flask(__name__)

DB_PATH = os.environ.get("DATABASE_PATH", "database.db")

# Global request counter — tracks requests served by THIS pod since startup
request_count = 0

# Shared CSS and nav used across all pages
BASE_STYLE = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        font-family: Arial, sans-serif;
        background: #0f172a;
        color: #e2e8f0;
        padding: 24px;
        max-width: 900px;
        margin: 0 auto;
    }
    h1 {
        color: #38bdf8;
        font-size: 24px;
        border-bottom: 2px solid #38bdf8;
        padding-bottom: 12px;
        margin-bottom: 8px;
    }
    .subtitle { font-size: 13px; color: #64748b; margin-bottom: 20px; }
    .nav {
        display: flex;
        gap: 6px;
        margin-bottom: 24px;
        flex-wrap: wrap;
    }
    .nav a {
        padding: 6px 14px;
        border-radius: 5px;
        border: 1px solid #334155;
        color: #94a3b8;
        font-size: 12px;
        text-decoration: none;
        background: #1e293b;
    }
    .nav a:hover { border-color: #38bdf8; color: #38bdf8; }
    .nav a.active { border-color: #38bdf8; color: #38bdf8; background: #0f172a; }
"""


# ===============================================
# DATABASE INITIALIZATION
# ===============================================

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


# ===============================================
# MAIN PAGE (CREATE + READ)
# ===============================================

@app.route("/", methods=["GET", "POST"])
def index():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if request.method == "POST":
        message = request.form["message"].strip()
        if message:
            c.execute("INSERT INTO messages (text) VALUES (?)", (message,))
            conn.commit()
        conn.close()
        return redirect("/")

    c.execute("SELECT * FROM messages ORDER BY created_at DESC")
    messages = c.fetchall()
    c.execute("SELECT COUNT(*) FROM messages")
    count = c.fetchone()[0]
    conn.close()

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Simple Cloud App</title>
    <style>
        {{ base_style }}
        .count-badge {
            display: inline-block;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 20px;
            padding: 4px 14px;
            font-size: 13px;
            color: #94a3b8;
            margin-bottom: 20px;
        }
        .count-badge span { color: #38bdf8; font-weight: bold; }
        .add-form { display: flex; gap: 8px; margin-bottom: 28px; }
        .add-form input {
            flex: 1;
            padding: 10px 14px;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 6px;
            color: #e2e8f0;
            font-size: 14px;
            outline: none;
        }
        .add-form input:focus { border-color: #38bdf8; }
        .add-form input::placeholder { color: #475569; }
        .btn {
            padding: 10px 18px;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
        }
        .btn-primary { background: #38bdf8; color: #0f172a; }
        .btn-primary:hover { background: #7dd3fc; }
        .btn-danger {
            background: transparent;
            border: 1px solid #ef4444;
            color: #ef4444;
            padding: 5px 10px;
            font-size: 12px;
            border-radius: 4px;
            cursor: pointer;
        }
        .btn-danger:hover { background: #ef4444; color: white; }
        .btn-edit {
            background: transparent;
            border: 1px solid #334155;
            color: #94a3b8;
            padding: 5px 10px;
            font-size: 12px;
            border-radius: 4px;
            text-decoration: none;
        }
        .btn-edit:hover { border-color: #38bdf8; color: #38bdf8; }
        .message-list { list-style: none; }
        .message-item {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 14px 16px;
            margin-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
        }
        .message-item:hover { border-color: #475569; }
        .message-text { flex: 1; font-size: 15px; color: #e2e8f0; }
        .message-time { font-size: 11px; color: #475569; margin-top: 4px; }
        .message-actions { display: flex; gap: 6px; align-items: center; flex-shrink: 0; }
        .empty-state {
            text-align: center;
            padding: 40px;
            color: #475569;
            font-size: 14px;
        }
    </style>
</head>
<body>

    <h1>&#9729; Simple Cloud App</h1>
    <p class="subtitle">Deployed on AWS EC2 &mdash; Kubernetes (k3s) &mdash; Docker</p>

    <nav class="nav">
        <a href="/" class="active">&#127968; App</a>
        <a href="/stats">&#128200; Live Monitor</a>
        <a href="/health">&#10084; Health</a>
    </nav>

    <div class="count-badge">Total messages: <span>{{ count }}</span></div>

    <form class="add-form" method="POST">
        <input name="message" placeholder="Type a message..." required>
        <button class="btn btn-primary" type="submit">Add</button>
    </form>

    {% if messages %}
    <ul class="message-list">
        {% for msg in messages %}
        <li class="message-item">
            <div>
                <div class="message-text">{{ msg[1] }}</div>
                <div class="message-time">Posted: {{ msg[2] }}</div>
            </div>
            <div class="message-actions">
                <a class="btn-edit" href="/edit/{{ msg[0] }}">Edit</a>
                <form action="/delete/{{ msg[0] }}" method="POST">
                    <button class="btn-danger" type="submit">Delete</button>
                </form>
            </div>
        </li>
        {% endfor %}
    </ul>
    {% else %}
    <div class="empty-state">No messages yet. Add one above.</div>
    {% endif %}

</body>
</html>
    """, messages=messages, count=count, base_style=BASE_STYLE)


# ===============================================
# DELETE MESSAGE
# ===============================================

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM messages WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")


# ===============================================
# UPDATE / EDIT MESSAGE
# ===============================================

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    if request.method == "POST":
        updated_text = request.form["message"].strip()
        if updated_text:
            c.execute("UPDATE messages SET text = ? WHERE id = ?", (updated_text, id))
            conn.commit()
        conn.close()
        return redirect("/")

    c.execute("SELECT * FROM messages WHERE id = ?", (id,))
    message = c.fetchone()
    conn.close()

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Edit Message</title>
    <style>
        {{ base_style }}
        .edit-form { display: flex; gap: 8px; margin-bottom: 16px; }
        .edit-form input {
            flex: 1;
            padding: 10px 14px;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 6px;
            color: #e2e8f0;
            font-size: 14px;
            outline: none;
        }
        .edit-form input:focus { border-color: #38bdf8; }
        .btn {
            padding: 10px 18px;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
        }
        .btn-primary { background: #38bdf8; color: #0f172a; }
        .btn-primary:hover { background: #7dd3fc; }
        .meta { font-size: 12px; color: #475569; margin-top: 8px; }
    </style>
</head>
<body>

    <h1>Edit Message</h1>
    <p class="subtitle">Update your message below</p>

    <nav class="nav">
        <a href="/">&#127968; App</a>
        <a href="/stats">&#128200; Live Monitor</a>
        <a href="/health">&#10084; Health</a>
    </nav>

    <form class="edit-form" method="POST">
        <input name="message" value="{{ message[1] }}" required>
        <button class="btn btn-primary" type="submit">Update</button>
    </form>
    <p class="meta">Originally posted: {{ message[2] }}</p>

</body>
</html>
    """, message=message, base_style=BASE_STYLE)


# ===============================================
# HEALTH CHECK
# ===============================================

@app.route("/health")
def health():
    hostname = socket.gethostname()
    try:
        pod_ip = socket.gethostbyname(hostname)
    except Exception:
        pod_ip = "unavailable"

    # Check database is reachable
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.cursor().execute("SELECT 1")
        conn.close()
        db_status = "ok"
    except Exception:
        db_status = "error"

    # Return JSON for Kubernetes liveness probe
    if request.headers.get("Accept", "").startswith("application/json") or \
       request.args.get("format") == "json":
        return jsonify({
            "status": "ok",
            "pod": hostname,
            "database": db_status,
            "db_path": DB_PATH
        }), 200

    # Return pretty HTML page for browser
    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>Health Check</title>
    <style>
        {{ base_style }}
        .health-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
            margin-bottom: 24px;
        }
        .health-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 18px;
        }
        .health-card .label {
            font-size: 11px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }
        .health-card .value {
            font-size: 22px;
            font-weight: bold;
            word-break: break-all;
        }
        .health-card .value.ok { color: #4ade80; }
        .health-card .value.error { color: #ef4444; }
        .health-card .value.info { color: #38bdf8; font-size: 15px; margin-top: 6px; }
        .status-banner {
            background: #14532d;
            border: 1px solid #4ade80;
            border-radius: 8px;
            padding: 16px 20px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .status-banner .icon { font-size: 24px; }
        .status-banner .text { font-size: 16px; font-weight: bold; color: #4ade80; }
        .status-banner .sub { font-size: 12px; color: #86efac; margin-top: 2px; }
        .json-box {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 16px 20px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            color: #94a3b8;
            line-height: 1.8;
        }
        .json-box .key { color: #38bdf8; }
        .json-box .val-ok { color: #4ade80; }
        .json-box .val-str { color: #fbbf24; }
        h2 {
            font-size: 11px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin: 24px 0 10px;
        }
    </style>
</head>
<body>

    <h1>&#10084; Health Check</h1>
    <p class="subtitle">Kubernetes liveness probe endpoint &mdash; GET /health</p>

    <nav class="nav">
        <a href="/">&#127968; App</a>
        <a href="/stats">&#128200; Live Monitor</a>
        <a href="/health" class="active">&#10084; Health</a>
    </nav>

    <div class="status-banner">
        <div class="icon">&#10003;</div>
        <div>
            <div class="text">All systems operational</div>
            <div class="sub">Application and database are responding normally</div>
        </div>
    </div>

    <div class="health-grid">
        <div class="health-card">
            <div class="label">App Status</div>
            <div class="value ok">OK</div>
        </div>
        <div class="health-card">
            <div class="label">Database</div>
            <div class="value {{ 'ok' if db_status == 'ok' else 'error' }}">
                {{ db_status | upper }}
            </div>
        </div>
        <div class="health-card">
            <div class="label">Pod Name</div>
            <div class="value info">{{ hostname }}</div>
        </div>
        <div class="health-card">
            <div class="label">Pod IP</div>
            <div class="value info">{{ pod_ip }}</div>
        </div>
    </div>

    <h2>Raw JSON Response</h2>
    <div class="json-box">
        {<br>
        &nbsp;&nbsp;<span class="key">"status"</span>: <span class="val-ok">"ok"</span>,<br>
        &nbsp;&nbsp;<span class="key">"pod"</span>: <span class="val-str">"{{ hostname }}"</span>,<br>
        &nbsp;&nbsp;<span class="key">"database"</span>: <span class="val-ok">"{{ db_status }}"</span>,<br>
        &nbsp;&nbsp;<span class="key">"db_path"</span>: <span class="val-str">"{{ db_path }}"</span><br>
        }
    </div>

</body>
</html>
    """,
    hostname=hostname,
    pod_ip=pod_ip,
    db_status=db_status,
    db_path=DB_PATH,
    base_style=BASE_STYLE
    )


# ===============================================
# MONITORING DASHBOARD
# ===============================================

@app.route("/stats")
def stats():
    import platform

    global request_count
    request_count += 1

    # Database stats
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM messages")
    total_messages = c.fetchone()[0]
    c.execute("SELECT text, created_at FROM messages ORDER BY created_at DESC LIMIT 1")
    last_msg = c.fetchone()
    c.execute("SELECT COUNT(*) FROM messages WHERE DATE(created_at) = DATE('now')")
    today_messages = c.fetchone()[0]
    conn.close()

    # Pod / system info
    hostname = socket.gethostname()
    try:
        pod_ip = socket.gethostbyname(hostname)
    except Exception:
        pod_ip = "unavailable"
    db_size = os.path.getsize(DB_PATH) if os.path.exists(DB_PATH) else 0
    db_size_kb = round(db_size / 1024, 2)

    # Kubernetes cluster info
    k8s_host      = os.environ.get("KUBERNETES_SERVICE_HOST", "not in cluster")
    k8s_port      = os.environ.get("KUBERNETES_SERVICE_PORT", "—")
    k8s_namespace = os.environ.get("POD_NAMESPACE", os.environ.get("NAMESPACE", "default"))
    node_name     = os.environ.get("NODE_NAME", "—")
    pod_name      = os.environ.get("POD_NAME", hostname)
    in_cluster    = k8s_host != "not in cluster"

    hpa_min    = "2"
    hpa_max    = "5"
    hpa_target = "50%"

    return render_template_string("""
<!DOCTYPE html>
<html>
<head>
    <title>App Monitor</title>
    <meta http-equiv="refresh" content="30">
    <style>
        {{ base_style }}
        h2 {
            color: #94a3b8;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin: 24px 0 10px;
        }
        .tabs { display: flex; gap: 4px; margin-bottom: 0; }
        .tab {
            padding: 8px 20px;
            border-radius: 6px 6px 0 0;
            border: 1px solid #334155;
            border-bottom: none;
            cursor: pointer;
            font-size: 13px;
            color: #94a3b8;
            background: #1e293b;
            user-select: none;
        }
        .tab.active {
            background: #0f172a;
            color: #38bdf8;
            border-color: #38bdf8;
            border-bottom: 1px solid #0f172a;
            margin-bottom: -1px;
        }
        .tab-border { border-top: 1px solid #334155; margin-bottom: 24px; }
        .tab-content { display: none; }
        .tab-content.active { display: block; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 14px;
        }
        .card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 18px;
        }
        .card .value {
            font-size: 28px;
            font-weight: bold;
            color: #38bdf8;
            margin: 6px 0 2px;
        }
        .card .label {
            font-size: 11px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .card.green .value { color: #4ade80; }
        .card.amber .value { color: #fbbf24; }
        .card.small .value { font-size: 15px; margin-top: 10px; word-break: break-all; }
        .pod-box {
            background: #1e293b;
            border: 2px solid #38bdf8;
            border-radius: 8px;
            padding: 16px;
        }
        .pod-name {
            font-size: 20px;
            font-weight: bold;
            color: #38bdf8;
            word-break: break-all;
        }
        .pod-detail { font-size: 13px; color: #94a3b8; margin-top: 6px; }
        .status-ok { color: #4ade80; font-weight: bold; }
        .k8s-table { width: 100%; border-collapse: collapse; }
        .k8s-table td {
            padding: 10px 14px;
            border-bottom: 1px solid #263548;
            font-size: 14px;
        }
        .k8s-table tr:last-child td { border-bottom: none; }
        .k8s-table td:first-child {
            color: #94a3b8;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            width: 40%;
        }
        .k8s-table td:last-child { color: #e2e8f0; font-weight: bold; }
        .k8s-section {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 14px;
        }
        .k8s-section-title {
            background: #263548;
            padding: 8px 14px;
            font-size: 11px;
            color: #38bdf8;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .last-msg {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 16px;
        }
        .last-msg .msg-text { font-size: 16px; color: #e2e8f0; margin-bottom: 6px; }
        .last-msg .msg-time { font-size: 12px; color: #64748b; }
        .note {
            background: #1e3a5f;
            border: 1px solid #38bdf8;
            border-radius: 6px;
            padding: 10px 14px;
            margin-top: 12px;
            font-size: 12px;
            color: #93c5fd;
        }
        .footer { margin-top: 28px; font-size: 11px; color: #475569; }
        .footer a { color: #38bdf8; text-decoration: none; }
    </style>
</head>
<body>

<h1>&#9679; Simple Cloud App &mdash; Live Monitor</h1>
<p class="subtitle">Real-time pod and cluster statistics</p>

<nav class="nav">
    <a href="/">&#127968; App</a>
    <a href="/stats" class="active">&#128200; Live Monitor</a>
    <a href="/health">&#10084; Health</a>
</nav>

<div class="tabs">
    <div class="tab" id="btn-app" onclick="showTab('app')">&#128200; App Stats</div>
    <div class="tab" id="btn-k8s" onclick="showTab('k8s')">&#9096; Cluster Info</div>
</div>
<div class="tab-border"></div>

<!-- TAB 1 — APP STATS -->
<div id="tab-app" class="tab-content">

    <h2>Pod Identity</h2>
    <div class="pod-box">
        <div class="pod-name">{{ hostname }}</div>
        <div class="pod-detail">Pod IP: {{ pod_ip }}</div>
        <div class="pod-detail">
            Requests served by this pod:
            <strong style="color:#38bdf8">{{ request_count }}</strong>
        </div>
        <div class="pod-detail">
            Status: <span class="status-ok">&#10003; RUNNING</span>
        </div>
    </div>
    <div class="note">
        Each Flask pod tracks its own request count independently.
        Refreshing may show a different pod name, IP, and counter &mdash;
        proving Kubernetes is load balancing across multiple pods.
    </div>

    <h2>Database Stats</h2>
    <div class="grid">
        <div class="card green">
            <div class="label">Total Messages</div>
            <div class="value">{{ total_messages }}</div>
        </div>
        <div class="card amber">
            <div class="label">Added Today</div>
            <div class="value">{{ today_messages }}</div>
        </div>
        <div class="card">
            <div class="label">Database Size</div>
            <div class="value">{{ db_size_kb }} KB</div>
        </div>
        <div class="card small">
            <div class="label">DB Location</div>
            <div class="value">{{ db_path }}</div>
        </div>
    </div>

    <h2>System Info</h2>
    <div class="grid">
        <div class="card">
            <div class="label">Python Version</div>
            <div class="value">{{ python_version }}</div>
        </div>
        <div class="card small">
            <div class="label">Platform</div>
            <div class="value">{{ platform_info }}</div>
        </div>
        <div class="card small">
            <div class="label">WSGI Server</div>
            <div class="value">Gunicorn</div>
        </div>
        <div class="card small">
            <div class="label">Orchestration</div>
            <div class="value">Kubernetes (k3s)</div>
        </div>
    </div>

    {% if last_msg %}
    <h2>Last Message</h2>
    <div class="last-msg">
        <div class="msg-text">{{ last_msg[0] }}</div>
        <div class="msg-time">Posted: {{ last_msg[1] }}</div>
    </div>
    {% endif %}

</div>

<!-- TAB 2 — CLUSTER INFO -->
<div id="tab-k8s" class="tab-content">

    <h2>Cluster Status</h2>
    <div class="grid">
        <div class="card green">
            <div class="label">In Cluster</div>
            <div class="value">{{ "Yes" if in_cluster else "No" }}</div>
        </div>
        <div class="card small">
            <div class="label">Namespace</div>
            <div class="value">{{ k8s_namespace }}</div>
        </div>
        <div class="card small">
            <div class="label">Node</div>
            <div class="value">{{ node_name }}</div>
        </div>
        <div class="card small">
            <div class="label">K8s API Host</div>
            <div class="value">{{ k8s_host }}</div>
        </div>
    </div>

    <h2>This Pod</h2>
    <div class="k8s-section">
        <div class="k8s-section-title">Pod Details</div>
        <table class="k8s-table">
            <tr><td>Pod Name</td><td>{{ pod_name }}</td></tr>
            <tr><td>Pod IP</td><td>{{ pod_ip }}</td></tr>
            <tr><td>Hostname</td><td>{{ hostname }}</td></tr>
            <tr><td>Requests Served</td><td>{{ request_count }}</td></tr>
        </table>
    </div>

    <h2>Horizontal Pod Autoscaler</h2>
    <div class="k8s-section">
        <div class="k8s-section-title">flask-hpa &mdash; Deployment/flask</div>
        <table class="k8s-table">
            <tr><td>Min Replicas</td><td>{{ hpa_min }}</td></tr>
            <tr><td>Max Replicas</td><td>{{ hpa_max }}</td></tr>
            <tr><td>CPU Scale Target</td><td>{{ hpa_target }}</td></tr>
            <tr><td>Scale Trigger</td><td>CPU utilisation &gt; 50% sustained</td></tr>
            <tr><td>Cool-down Period</td><td>5 minutes (default)</td></tr>
        </table>
    </div>

    <h2>Service Configuration</h2>
    <div class="k8s-section">
        <div class="k8s-section-title">Network</div>
        <table class="k8s-table">
            <tr><td>Flask Service</td><td>ClusterIP &mdash; internal only (port 5000)</td></tr>
            <tr><td>Nginx Service</td><td>NodePort &mdash; public (port 30080)</td></tr>
            <tr><td>Health Probe</td><td>GET /health every 10s</td></tr>
            <tr><td>Storage</td><td>PersistentVolumeClaim &mdash; 1Gi at /data</td></tr>
        </table>
    </div>

    <div class="note">
        Kubernetes environment variables (KUBERNETES_SERVICE_HOST, NODE_NAME, POD_NAME)
        are automatically injected into every pod by k3s, allowing the application to
        discover its own cluster context at runtime without any hardcoded configuration.
    </div>

</div>

<p class="footer">
    Auto-refreshes every 30 seconds &nbsp;|&nbsp;
    <a href="/">&#8592; Back to App</a>
</p>

<script>
    function showTab(name) {
        document.querySelectorAll('.tab-content').forEach(function(el) {
            el.classList.remove('active');
        });
        document.querySelectorAll('.tab').forEach(function(el) {
            el.classList.remove('active');
        });
        document.getElementById('tab-' + name).classList.add('active');
        document.getElementById('btn-' + name).classList.add('active');
        window.location.hash = name;
    }

    window.onload = function() {
        var hash = window.location.hash.replace('#', '');
        if (hash === 'k8s') {
            showTab('k8s');
        } else {
            showTab('app');
        }
    };
</script>

</body>
</html>
    """,
    hostname=hostname,
    pod_ip=pod_ip,
    pod_name=pod_name,
    request_count=request_count,
    total_messages=total_messages,
    today_messages=today_messages,
    db_size_kb=db_size_kb,
    db_path=DB_PATH,
    last_msg=last_msg,
    python_version=platform.python_version(),
    platform_info=platform.system() + " " + platform.release(),
    k8s_host=k8s_host,
    k8s_port=k8s_port,
    k8s_namespace=k8s_namespace,
    node_name=node_name,
    in_cluster=in_cluster,
    hpa_min=hpa_min,
    hpa_max=hpa_max,
    hpa_target=hpa_target,
    base_style=BASE_STYLE
    )


# ===============================================
# START APPLICATION
# ===============================================
init_db()
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
