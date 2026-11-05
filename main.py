import os
import re
import requests
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Video Downloader</title>
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
      margin-bottom: 12px;
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
    <p class="sub">Paste YouTube video link to download instantly</p>

    <div class="input-box">
      <input type="text" id="url" placeholder="https://youtu.be/..." autocomplete="off">
      <button id="btn" onclick="fetchVideo()">Get Download Link</button>
    </div>

    <div id="loader">Fetching video, please wait...</div>
    <div id="msg" class="err"></div>

    <div id="result">
      <img id="thumb" class="thumb" src="" alt="Thumbnail">
      <div id="vidTitle" class="title"></div>
      <a id="downloadBtn" class="dl-btn" href="" target="_blank" rel="noopener noreferrer">Download Video Now</a>
    </div>
  </div>

  <script>
    async function fetchVideo() {
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
        const res = await fetch("/api/info", {
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
          msg.innerText = data.error || "Video download link generate nahi ho paya.";
        }
      } catch (e) {
        msg.innerText = "Server connection error.";
      } finally {
        loader.style.display = "none";
        btn.disabled = false;
      }
    }
  </script>
</body>
</html>
"""

def extract_id(url):
    pattern = r'(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

@app.route("/")
def home():
    return render_template_string(HTML_PAGE)

@app.route("/api/info", methods=["POST"])
def get_info():
    data = request.get_json(silent=True) or {}
    url = data.get("url")
    if not url:
        return jsonify({"error": "URL provide karein"}), 400

    vid_id = extract_id(url)
    if not vid_id:
        return jsonify({"error": "Aapka link valid YouTube link nahi hai"}), 400

    # High speed YouTube fetcher endpoints
    try:
        api_url = f"https://api.vkrdownloader.workers.dev/server?v={url}"
        r = requests.get(api_url, timeout=10)
        res = r.json()

        if res.get("data") and res["data"].get("downloads"):
            downloads = res["data"]["downloads"]
            # Video stream filter (mp4 preferred)
            mp4_formats = [d for d in downloads if d.get("format_id") and "mp4" in d.get("format_id", "").lower() and d.get("url")]
            download_url = mp4_formats[0]["url"] if mp4_formats else downloads[0].get("url")

            return jsonify({
                "title": res["data"].get("title", "YouTube Video"),
                "thumbnail": res["data"].get("thumbnail", f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg"),
                "download_url": download_url
            })
    except Exception:
        pass

    # Fallback endpoint
    try:
        api_url2 = f"https://yt-api-service.onrender.com/download?id={vid_id}"
        r2 = requests.get(api_url2, timeout=8)
        res2 = r2.json()
        if res2.get("url"):
            return jsonify({
                "title": res2.get("title", "YouTube Video"),
                "thumbnail": f"https://img.youtube.com/vi/{vid_id}/hqdefault.jpg",
                "download_url": res2.get("url")
            })
    except Exception:
        pass

    return jsonify({"error": "YouTube ke server ne is video ka format block kiya hua hai. Dusra link try karein."}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
