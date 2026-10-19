# -*- coding: utf-8 -*-
from flask import Flask, request, Response
import random, urllib3
import 红果短剧 as hg

urllib3.disable_warnings()
app = Flask(__name__)
hg._STREAM_MAX_SESSIONS = 64

@app.route("/")
def home():
    return "Stream Node Ready", 200

@app.route("/media_pipe")
def stream_video():
    vid = request.args.get("vid", "").strip()
    if not vid:
        return "missing vid", 400
    try:
        did = str(random.randint(10**17, 10**18 - 1))
        iid = str(random.randint(10**17, 10**18 - 1))
        session = hg._stream_session(vid, {"device_id": did, "install_id": iid})
    except Exception as e:
        return f"stream error: {e}", 502

    raw_range = request.headers.get("Range") or ""
    requested = hg._parse_range(raw_range, session.total)
    if requested is hg._RANGE_UNSATISFIABLE:
        return Response(b"", status=416, headers={"Content-Range": f"bytes */{session.total}"})

    start, end = requested if requested else (0, session.total - 1)
    headers = {
        "Content-Type": "video/mp4",
        "Accept-Ranges": "bytes",
        "Content-Length": str(end - start + 1),
        "Access-Control-Allow-Origin": "*",
    }
    if requested:
        headers["Content-Range"] = f"bytes {start}-{end}/{session.total}"

    return Response(session.iter_range(start, end), status=206 if requested else 200, headers=headers, direct_passthrough=True)