import os
import math
import glob
import shutil
import tempfile
import subprocess
from flask import Flask, render_template_string, request, redirect, jsonify
import cloudinary
import cloudinary.uploader
import cloudinary.api
import imageio_ffmpeg

app = Flask(__name__)

# --- CONFIGURATION ---
cloudinary.config(
    cloud_name="dntmgunma",
    api_key="247386995162694",
    api_secret="Z4NDEGSgXqA5eUdNlRbjL6V-FoE"
)

PASSWORD_PROTECT = "809047"
FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()

# --- MODERN UI TEMPLATES ---
HTML_MAIN = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Jio Video Cloud Pro</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        :root {
            --bg: #090d16;
            --card: #121826;
            --card-border: #1e293b;
            --text: #f8fafc;
            --muted: #94a3b8;
            --accent: #3b82f6;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: var(--bg);
            color: var(--text);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            padding-bottom: 40px;
        }
        .header {
            background: rgba(18, 24, 38, 0.92);
            backdrop-filter: blur(12px);
            padding: 16px 20px;
            border-bottom: 1px solid var(--card-border);
            position: sticky;
            top: 0;
            z-index: 100;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .brand {
            font-size: 19px;
            font-weight: 800;
            background: linear-gradient(90deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .dev-badge {
            font-size: 11px;
            background: rgba(239, 68, 68, 0.15);
            color: #f87171;
            padding: 4px 10px;
            border-radius: 20px;
            border: 1px solid rgba(239, 68, 68, 0.3);
            font-weight: 600;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 16px;
        }
        .search-form {
            display: flex;
            gap: 8px;
            margin-bottom: 20px;
        }
        .search-input {
            flex: 1;
            padding: 12px 16px;
            border-radius: 12px;
            border: 1px solid var(--card-border);
            background: var(--card);
            color: var(--text);
            font-size: 14px;
            outline: none;
        }
        .search-input:focus { border-color: var(--accent); }
        .search-btn {
            padding: 0 20px;
            border-radius: 12px;
            border: none;
            background: var(--accent);
            color: #fff;
            font-weight: 700;
            cursor: pointer;
        }
        .upload-card {
            background: var(--card);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 24px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
        }
        .card-title {
            font-size: 16px;
            font-weight: 700;
            margin-bottom: 14px;
            color: #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .chunk-tag {
            font-size: 11px;
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            padding: 3px 8px;
            border-radius: 6px;
        }
        .input-field {
            width: 100%;
            padding: 11px 14px;
            margin-bottom: 12px;
            border-radius: 10px;
            border: 1px solid var(--card-border);
            background: #0b101b;
            color: var(--text);
            font-size: 14px;
        }
        .file-box {
            border: 2px dashed #334155;
            border-radius: 12px;
            padding: 14px;
            text-align: center;
            margin-bottom: 10px;
            background: rgba(15, 23, 42, 0.5);
        }
        input[type="file"] {
            width: 100%;
            color: var(--muted);
            font-size: 13px;
        }
        .detect-info {
            font-size: 12px;
            color: #60a5fa;
            margin-bottom: 12px;
            display: none;
            background: rgba(59, 130, 246, 0.1);
            padding: 8px 12px;
            border-radius: 8px;
            border: 1px solid rgba(59, 130, 246, 0.25);
        }
        .btn-upload {
            width: 100%;
            padding: 13px;
            border-radius: 12px;
            border: none;
            background: linear-gradient(135deg, #3b82f6, #6366f1);
            color: #fff;
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 0.5px;
            cursor: pointer;
            box-shadow: 0 4px 14px rgba(59, 130, 246, 0.4);
        }
        .btn-upload:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
        .progress-container {
            width: 100%;
            background: #1e293b;
            border-radius: 10px;
            overflow: hidden;
            margin: 12px 0 6px;
            display: none;
            height: 10px;
        }
        .progress-bar {
            width: 0%;
            height: 100%;
            background: linear-gradient(90deg, #10b981, #34d399);
            transition: width 0.2s ease;
        }
        #statusText {
            font-size: 12px;
            color: #34d399;
            text-align: center;
            margin-bottom: 8px;
            font-weight: 600;
        }
        .video-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 16px;
        }
        .v-card {
            background: var(--card);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .thumb-wrap {
            position: relative;
            width: 100%;
            aspect-ratio: 16 / 9;
            background: #000;
        }
        .thumb {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .v-body {
            padding: 14px;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .v-title {
            font-size: 14px;
            font-weight: 700;
            color: #f1f5f9;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .btn-group {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
        }
        .btn {
            padding: 9px 10px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 700;
            text-align: center;
            text-decoration: none;
            color: #fff;
        }
        .btn-play { background: var(--success); }
        .btn-dl { background: var(--warning); color: #000; }
        .btn-ren { background: #334155; color: #e2e8f0; }
        .btn-del { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.35); }
        .pagination {
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-top: 28px;
        }
        .nav-btn {
            padding: 11px 20px;
            border-radius: 12px;
            text-decoration: none;
            font-size: 13px;
            font-weight: 700;
            background: var(--card);
            color: #60a5fa;
            border: 1px solid var(--card-border);
        }
        .nav-btn.primary {
            background: var(--accent);
            color: #fff;
            border: none;
        }
    </style>
</head>
<body>

<div class="header">
    <span class="brand">Jio Video Cloud Pro</span>
    <span class="dev-badge">Atif Khan</span>
</div>

<div class="container">
    <form action="/" method="GET" class="search-form">
        <input type="text" name="q" class="search-input" placeholder="Search videos by name..." value="{{ q }}">
        <button type="submit" class="search-btn">Search</button>
    </form>

    <div class="upload-card">
        <div class="card-title">
            <span>Upload New Video</span>
            <span class="chunk-tag">Auto-Split > 95MB</span>
        </div>
        <input type="text" id="customName" class="input-field" placeholder="Video Name (e.g. Movie)">
        <div class="file-box">
            <input type="file" id="fileInput" accept="video/*" onchange="checkFileSize()">
        </div>
        <div id="detectInfo" class="detect-info"></div>
        <div class="progress-container" id="progCont"><div class="progress-bar" id="progBar"></div></div>
        <div id="statusText"></div>
        <button id="upBtn" onclick="startUpload()" class="btn-upload">UPLOAD TO CLOUD</button>
    </div>

    <div class="video-grid">
        {% for v in videos %}
        <div class="v-card">
            <div class="thumb-wrap">
                <img src="{{ v.thumb_url }}" class="thumb" loading="lazy">
            </div>
            <div class="v-body">
                <div class="v-title" title="{{ v.public_id }}">{{ v.public_id }}</div>
                <div class="btn-group">
                    <a href="{{ v.secure_url }}" class="btn btn-play">▶ PLAY</a>
                    <a href="{{ v.dl_url }}" class="btn btn-dl">⬇ DOWNLOAD</a>
                    <a href="/verify/rename/{{ v.public_id }}" class="btn btn-ren">✎ RENAME</a>
                    <a href="/verify/delete/{{ v.public_id }}" class="btn btn-del">🗑 DELETE</a>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>

    <div class="pagination">
        <a href="/" class="nav-btn">⌂ HOME</a>
        {% if next_cursor %}<a href="/?cursor={{ next_cursor }}&q={{ q }}" class="nav-btn primary">NEXT PAGE →</a>{% endif %}
    </div>
</div>

<script>
const LIMIT_MB = 95;
const LIMIT_BYTES = LIMIT_MB * 1024 * 1024;

function checkFileSize() {
    const file = document.getElementById('fileInput').files[0];
    const info = document.getElementById('detectInfo');
    if (!file) { info.style.display = 'none'; return; }

    const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
    const baseName = document.getElementById('customName').value.trim() || file.name.replace(/\.[^/.]+$/, "");
    info.style.display = 'block';

    if (file.size <= LIMIT_BYTES) {
        info.innerHTML = `✅ Size: <b>${sizeMB} MB</b> (100MB se kam hai — Seedha Direct Upload hoga)`;
    } else {
        const parts = Math.ceil(file.size / (90 * 1024 * 1024));
        let names = [];
        for (let i = 1; i <= parts; i++) names.push(`${baseName}_p${i}`);
        info.innerHTML = `⚡ Size: <b>${sizeMB} MB</b> (100MB se badi hai — Auto Split hokar <b>${parts} parts</b> banenge: ${names.join(', ')})`;
    }
}

async function startUpload() {
    const file = document.getElementById('fileInput').files[0];
    const customName = document.getElementById('customName').value.trim();
    const btn = document.getElementById('upBtn');
    if (!file) { alert("File chuniye!"); return; }

    btn.disabled = true;
    document.getElementById('progCont').style.display = 'block';

    // CASE 1: <= 95 MB -> Direct Upload to Cloudinary
    if (file.size <= LIMIT_BYTES) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('upload_preset', 'ml_default');
        if (customName) formData.append('public_id', customName);

        const xhr = new XMLHttpRequest();
        xhr.open('POST', 'https://api.cloudinary.com/v1_1/dntmgunma/video/upload');
        xhr.upload.onprogress = (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                document.getElementById('progBar').style.width = percent + '%';
                document.getElementById('statusText').innerText = percent + '% Direct Uploading...';
            }
        };
        xhr.onload = () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                alert("Direct Upload Complete!");
                location.reload();
            } else {
                alert("Upload Failed: " + xhr.responseText);
                btn.disabled = false;
            }
        };
        xhr.onerror = () => { alert("Network Error"); btn.disabled = false; };
        xhr.send(formData);
        return;
    }

    // CASE 2: > 95 MB -> Send to Server to Auto-Split into p1, p2, p3... & Upload
    const baseName = customName || file.name.replace(/\.[^/.]+$/, "");
    const formData = new FormData();
    formData.append('file', file);
    formData.append('base_name', baseName);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/split-upload');
    xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);
            document.getElementById('progBar').style.width = percent + '%';
            if (percent < 100) {
                document.getElementById('statusText').innerText = `Step 1/2: File bhej rahe hain (${percent}%)...`;
            } else {
                document.getElementById('statusText').innerText = `Step 2/2: Video ko p1, p2, p3 parts mein tod kar Cloud par upload kar rahe hain (Wait karein)...`;
            }
        }
    };
    xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) {
            const res = JSON.parse(xhr.responseText);
            alert("Success! Uploaded Parts: " + res.parts.join(", "));
            location.reload();
        } else {
            alert("Split Upload Error: " + xhr.responseText);
            btn.disabled = false;
        }
    };
    xhr.onerror = () => { alert("Server Connection Error"); btn.disabled = false; };
    xhr.send(formData);
}
</script>
</body>
</html>
"""

HTML_VERIFY = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: #090d16;
            color: #f8fafc;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }
        .box {
            width: 100%;
            max-width: 400px;
            background: #121826;
            border: 1px solid #1e293b;
            border-radius: 18px;
            padding: 28px 22px;
            text-align: center;
            box-shadow: 0 15px 35px rgba(0,0,0,0.5);
        }
        h3 { font-size: 20px; margin-bottom: 8px; color: #f1f5f9; }
        .meta {
            font-size: 12px;
            color: #94a3b8;
            background: #0b101b;
            padding: 8px 12px;
            border-radius: 8px;
            margin-bottom: 18px;
            word-break: break-all;
        }
        input {
            width: 100%;
            padding: 12px 14px;
            background: #0b101b;
            color: #fff;
            border: 1px solid #334155;
            border-radius: 10px;
            margin-bottom: 12px;
            font-size: 14px;
            outline: none;
        }
        input:focus { border-color: #3b82f6; }
        .btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #10b981, #059669);
            color: #fff;
            border: none;
            border-radius: 10px;
            font-weight: 700;
            font-size: 14px;
            cursor: pointer;
            margin-top: 4px;
        }
        .cancel {
            display: inline-block;
            margin-top: 16px;
            color: #94a3b8;
            text-decoration: none;
            font-size: 13px;
        }
    </style>
</head>
<body>
    <div class="box">
        <h3>Security Verification</h3>
        <div class="meta">Action: <b>{{ action|upper }}</b><br>Target: {{ target_id }}</div>
        <form action="/process/{{ action }}/{{ target_id }}" method="POST">
            <input type="password" name="pw" placeholder="Enter Admin Password" required>
            {% if action == 'rename' %}
            <input type="text" name="new_name" placeholder="Enter New Video Name" required>
            {% endif %}
            <button type="submit" class="btn">CONFIRM ACTION</button>
        </form>
        <a href="/" class="cancel">← Cancel & Go Back</a>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    query = request.args.get('q', '').strip()
    cursor = request.args.get('cursor')
    try:
        res = cloudinary.api.resources(resource_type="video", type="upload", max_results=10, next_cursor=cursor)
        raw_videos = res.get('resources', [])
        next_cursor = res.get('next_cursor')
        videos = []
        for v in raw_videos:
            if query and query.lower() not in v['public_id'].lower():
                continue
            url = v.get('secure_url', '')
            v['thumb_url'] = url.rsplit('.', 1)[0] + '.jpg' if '.' in url else url
            v['dl_url'] = url.replace('/upload/', '/upload/fl_attachment/')
            videos.append(v)
        return render_template_string(HTML_MAIN, videos=videos, q=query, next_cursor=next_cursor)
    except Exception as e:
        return f"Error loading videos: {e}"

@app.route('/split-upload', methods=['POST'])
def split_upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file received"}), 400
    
    file = request.files['file']
    base_name = request.form.get('base_name', 'Video').strip()
    base_name = "".join(c for c in base_name if c.isalnum() or c in ('-', '_')).strip() or "Video"

    tmp_dir = tempfile.mkdtemp()
    try:
        input_path = os.path.join(tmp_dir, "input.mp4")
        file.save(input_path)

        total_size = os.path.getsize(input_path)
        # Calculate number of parts (~90MB each so every part is safely < 100MB)
        num_parts = max(2, math.ceil(total_size / (90 * 1024 * 1024)))

        # Get total video duration using ffmpeg
        probe = subprocess.run([FFMPEG_PATH, "-i", input_path], stderr=subprocess.PIPE, text=True)
        duration = 0
        for line in probe.stderr.splitlines():
            if "Duration:" in line:
                t_str = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = t_str.split(":")
                duration = int(h) * 3600 + int(m) * 60 + float(s)
                break

        part_duration = math.ceil(duration / num_parts) if duration > 0 else 600
        uploaded_parts = []

        for i in range(num_parts):
            start_sec = i * part_duration
            part_name = f"{base_name}_p{i + 1}"
            out_path = os.path.join(tmp_dir, f"{part_name}.mp4")

            cmd = [
                FFMPEG_PATH, "-y",
                "-ss", str(start_sec),
                "-i", input_path,
                "-t", str(part_duration),
                "-c", "copy",
                "-avoid_negative_ts", "1",
                out_path
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            if os.path.exists(out_path) and os.path.getsize(out_path) > 1024:
                cloudinary.uploader.upload(
                    out_path,
                    resource_type="video",
                    public_id=part_name,
                    overwrite=True
                )
                uploaded_parts.append(part_name)
                os.remove(out_path)

        return jsonify({"status": "ok", "parts": uploaded_parts})
    except Exception as e:
        return str(e), 500
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@app.route('/verify/<action>/<path:target_id>')
def verify(action, target_id):
    return render_template_string(HTML_VERIFY, action=action, target_id=target_id)

@app.route('/process/<action>/<path:target_id>', methods=['POST'])
def process(action, target_id):
    pw = request.form.get('pw')
    if pw != PASSWORD_PROTECT:
        return "<h3>Wrong Password! <a href='/'>Go Back</a></h3>"
    
    if action == 'delete':
        cloudinary.uploader.destroy(target_id, resource_type="video")
    elif action == 'rename':
        new_name = request.form.get('new_name').strip()
        cloudinary.uploader.rename(target_id, new_name, resource_type="video")
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
