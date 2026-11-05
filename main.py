import os
import glob
from flask import Flask, request, jsonify, render_template_string, send_file
import static_ffmpeg
import yt_dlp

# Render par ffmpeg load karein
static_ffmpeg.add_paths()

app = Flask(__name__)

DOWNLOAD_DIR = os.path.join(os.getcwd(), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>YouTube Downloader</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: radial-gradient(circle at top, #1e1b4b 0%, #09090b 100%);
      color: #f4f4f5;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .card {
      width: 100%;
      max-width: 500px;
      background: rgba(24, 24, 27, 0.9);
      backdrop-filter: blur(16px);
      border: 1px solid rgba(255, 255, 255, 0.1);
      border-radius: 20px;
      padding: 32px 24px;
      box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
    }
    h1 {
      font-size: 24px;
      font-weight: 700;
      text-align: center;
      margin-bottom: 6px;
      background: linear-gradient(135deg, #a855f7, #6366f1);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    p.sub {
      text-align: center;
      color: #a1a1aa;
      font-size: 13px;
      margin-bottom: 24px;
    }
    .input-box {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    input {
      width: 100%;
      padding: 14px 16px;
      border-radius: 12px;
      border: 1px solid #3f3f46;
      background: #18181b;
      color: #fff;
      font-size: 14px;
      outline: none;
    }
    input:focus {
      border-color: #6366f1;
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
    }
    button {
      padding: 14px;
      border-radius: 12px;
      border: none;
      background: linear-gradient(135deg, #6366f1, #a855f7);
      color: #fff;
      font-weight: 600;
      font-size: 14px;
      cursor: pointer;
    }
    button:disabled { opacity: 0.6; cursor: not-allowed; }
    #loader {
      display: none;
      text-align: center;
      margin-top: 18px;
      font-size: 13px;
      color: #c084fc;
    }
    #result {
      margin-top: 20px;
      display: none;
      background: #27272a;
      border-radius: 14px;
      padding: 16px;
      border: 1px solid #3f3f46;
      text-align: center;
    }
    .thumb {
      width: 100%;
      border-radius: 10px;
      margin-bottom: 12px;
      max-height: 200px;
      object-fit: cover;
    }
    .title {
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 14px;
      color: #fafafa;
    }
    .dl-btn {
      display: inline-block;
      width: 100%;
      text-align: center;
      text-decoration: none;
      background: #10b981;
      color: white;
      padding: 12px;
      border-radius: 10px;
      font-weight: 600;
      font-size: 14px;
    }
    .err {
      color: #f87171;
      font-size: 13px;
      text-align: center;
      margin-top: 14px;
      line-height: 1.4;
    }
  </style>
</head>
<body>
  <div class="card">
    <h1>Video Downloader</h1>
    <p class="sub">Paste YouTube video link to download MP4</p>

    <div class="input-box">
      <input type="text" id="url" placeholder="https://youtu.be/..." autocomplete="off">
      <button id="btn" onclick="processVideo()">Download Video</button>
    </div>

    <div id="loader">Processing & merging video, please wait 10-20 seconds...</div>
    <div id="msg" class="err"></div>

    <div id="result">
      <img id="thumb" class="thumb" src="" alt="Thumbnail">
      <div id="vidTitle" class="title"></div>
      <a id="downloadBtn" class="dl-btn" href="" download>Save MP4 to Device</a>
    </div>
  </div>

  <script>
    async function processVideo() {
      const url = document.getElementById("url").value.trim();
      const loader = document.getElementById("loader");
      const msg = document.getElementById("msg");
      const result = document.getElementById("result");
      const btn = document.getElementById("btn");

      msg.innerText = "";
      result.style.display = "none";

      if (!url) {
        msg.innerText = "Kripya YouTube URL dalein!";
        return;
      }

      btn.disabled = true;
      loader.style.display = "block";

      try {
        const res = await fetch("/api/process", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: url })
        });
        const data = await res.json();

        if (res.ok && data.download_url) {
          document.getElementById("thumb").src = data.thumbnail || "";
          document.getElementById("vidTitle").innerText = data.title;
          document.getElementById("downloadBtn").href = data.download_url;
          result.style.display = "block";
        } else {
          msg.innerText = data.error || "Video process nahi ho saki.";
        }
      } catch (e) {
        msg.innerText = "Server error, dobara try karein.";
      } finally {
        loader.style.display = "none";
        btn.disabled = false;
      }
    }
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/api/process", methods=["POST"])
def process():
    data = request.get_json(silent=True) or {}
    url = data.get("url")
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    # Old downloads clean karein taaki storage full na ho
    for f in glob.glob(os.path.join(DOWNLOAD_DIR, "*")):
        try:
            os.remove(f)
        except Exception:
            pass

    out_template = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")
    cookie_file = "cookies.txt" if os.path.exists("cookies.txt") else None

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': out_template,
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
    }

    if cookie_file:
        ydl_opts['cookiefile'] = cookie_file

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get("id")
            title = info.get("title", "video")
            thumbnail = info.get("thumbnail", "")

            final_file = f"{video_id}.mp4"
            return jsonify({
                "title": title,
                "thumbnail": thumbnail,
                "download_url": f"/get-file/{final_file}"
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/get-file/<filename>")
def get_file(filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return "File not found", 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
