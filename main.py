import os
from flask import Flask, render_template_string, request, redirect, url_for
import cloudinary
import cloudinary.uploader
import cloudinary.api

app = Flask(__name__)

# --- CONFIGURATION ---
cloudinary.config( 
  cloud_name = "dntmgunma", 
  api_key = "247386995162694", 
  api_secret = "Z4NDEGSgXqA5eUdNlRbjL6V-FoE" 
)

PASSWORD_PROTECT = "809047"

# HTML Templates
HTML_MAIN = """
<!DOCTYPE html>
<html>
<head>
    <title>Jio Video Cloud Pro</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; text-align: center; padding: 0; margin: 0; }
        .header { background: #cc0000; padding: 15px; border-bottom: 3px solid #900; }
        .main-title { font-size: 20px; font-weight: bold; }
        .dev-name { font-size: 12px; color: #ffc107; display: block; margin-top: 4px; }
        .box { border: 2px dashed #444; padding: 15px; margin: 10px; background: #111; }
        input[type="text"], input[type="file"] { width: 90%; padding: 10px; margin: 5px 0; background: #222; border: 1px solid #444; color: #fff; }
        .progress-container { width: 90%; background: #333; margin: 10px auto; display: none; height: 15px; }
        .progress-bar { width: 0%; height: 100%; background: #28a745; }
        .v-card { border-bottom: 2px solid #222; padding: 15px 5px; margin: 10px; background: #0a0a0a; }
        .thumb { width: 160px; height: 110px; object-fit: cover; border: 1px solid #333; }
        .btn { padding: 10px; border: none; font-weight: bold; color: #fff; margin: 5px; width: 45%; font-size: 12px; border-radius: 4px; text-decoration:none; display:inline-block; }
        .btn-up { background: #28a745; width: 95%; }
        .btn-dl { background: #007bff; }
        .btn-ren { background: #ffc107; color: #000; }
        .btn-del { background: #dc3545; width: 93%; }
        .search-box { background: #111; padding: 10px; border-bottom: 1px solid #cc0000; }
        .nav-btn { color: #ffc107; text-decoration: none; font-weight: bold; padding: 10px; border: 1px solid #444; margin: 5px; display: inline-block; }
    </style>
</head>
<body>
    <div class="header">
        <span class="main-title">Jio Video Cloud</span>
        <span class="dev-name">Developed by: ATIF KHAN</span>
    </div>

    <div class="search-box">
        <form action="/" method="GET">
            <input type="text" name="q" placeholder="Search..." value="{{ q }}" style="width:60%;">
            <button type="submit" style="padding:10px; background:#cc0000; color:#fff; border:none;">GO</button>
        </form>
    </div>

    <div class="box">
        <b>Upload Video</b><br>
        <input type="text" id="videoName" placeholder="Video Name">
        <input type="file" id="fileInput">
        <div class="progress-container" id="progCont"><div class="progress-bar" id="progBar"></div></div>
        <div id="status" style="font-size:11px;"></div>
        <button onclick="startUpload()" class="btn btn-up">UPLOAD NOW</button>
    </div>

    {% for v in videos %}
    <div class="v-card">
        <b style="color: #ffc107;">{{ v.public_id }}</b><br>
        <img src="{{ v.secure_url.replace('.mp4', '.jpg').replace('.mkv', '.jpg').replace('.3gp', '.jpg') }}" class="thumb"><br>
        <a href="{{ v.secure_url }}" class="btn btn-dl">DOWNLOAD</a>
        <a href="/verify/rename/{{ v.public_id }}" class="btn btn-ren">RENAME</a>
        <a href="/verify/delete/{{ v.public_id }}" class="btn btn-del">DELETE VIDEO</a>
    </div>
    {% endfor %}

    <div class="nav-box">
        {% if next_cursor %} <a href="/?cursor={{ next_cursor }}{% if q %}&q={{ q }}{% endif %}" class="nav-btn">NEXT >></a> {% endif %}
        <br><br><a href="/" class="nav-btn" style="background:#333;">HOME</a>
    </div>

<script>
async function startUpload() {
    const file = document.getElementById('fileInput').files[0];
    const vName = document.getElementById('videoName').value;
    if (!file || !vName) { alert("Fill details!"); return; }

    document.getElementById('progCont').style.display = 'block';
    const formData = new FormData();
    formData.append('file', file);
    formData.append('upload_preset', 'ml_default');
    formData.append('public_id', vName);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', 'https://api.cloudinary.com/v1_1/dntmgunma/video/upload');
    xhr.upload.onprogress = (e) => {
        const percent = Math.round((e.loaded / e.total) * 100);
        document.getElementById('progBar').style.width = percent + '%';
        document.getElementById('status').innerText = percent + "% Uploading...";
    };
    xhr.onload = () => { if(xhr.status===200){ alert("Done!"); location.reload(); } };
    xhr.send(formData);
}
</script>
</body>
</html>
"""

HTML_VERIFY = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #000; color: #fff; font-family: sans-serif; text-align: center; padding-top: 50px; }
        .v-box { border: 1px solid #cc0000; padding: 20px; margin: 20px; background: #111; }
        input { padding: 10px; width: 80%; margin: 10px 0; }
        .btn { padding: 10px 20px; background: #cc0000; color: #fff; border: none; font-weight: bold; }
    </style>
</head>
<body>
    <div class="v-box">
        <h3>Security Check</h3>
        <p>Action: {{ action_type }} ({{ target_id }})</p>
        <form action="/process/{{ action_type }}/{{ target_id }}" method="POST">
            <input type="password" name="pass" placeholder="Enter Password" required><br>
            {% if action_type == 'rename' %}
            <input type="text" name="new_name" placeholder="Enter New Name" required><br>
            {% endif %}
            <button type="submit" class="btn">CONFIRM</button>
        </form>
        <br><a href="/" style="color:#888;">Cancel</a>
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
        videos = res.get('resources', [])
        next_cursor = res.get('next_cursor')
        if query:
            videos = [v for v in videos if query.lower() in v['public_id'].lower()]
        return render_template_string(HTML_MAIN, videos=videos, q=query, next_cursor=next_cursor)
    except: return "Error loading videos."

@app.route('/verify/<action>/<target_id>')
def verify(action, target_id):
    return render_template_string(HTML_VERIFY, action_type=action, target_id=target_id)

@app.route('/process/<action>/<target_id>', methods=['POST'])
def process(action, target_id):
    p = request.form.get('pass')
    if p != PASSWORD_PROTECT: return "<h1>Wrong Password!</h1><br><a href='/'>Back</a>"
    
    if action == 'delete':
        cloudinary.uploader.destroy(target_id, resource_type="video")
    elif action == 'rename':
        new_name = request.form.get('new_name')
        cloudinary.uploader.rename(target_id, new_name, resource_type="video")
    
    return redirect('/')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
