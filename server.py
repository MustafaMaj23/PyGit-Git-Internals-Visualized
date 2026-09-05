import os
import zlib
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

OBJECTS_DIR = os.path.join(".pygit", "objects")
HEAD_PATH = os.path.join(".pygit", "HEAD")

def read_object(sha1):
    obj_path = os.path.join(OBJECTS_DIR, sha1[:2], sha1[2:])
    with open(obj_path, "rb") as f:
        raw = zlib.decompress(f.read())
    null_idx = raw.find(b"\0")
    header = raw[:null_idx].decode()
    obj_type, _ = header.split(" ")
    data = raw[null_idx + 1:]
    return obj_type, data

@app.route('/api/commits', methods=['GET'])
def get_commits():
    if not os.path.exists(HEAD_PATH):
        return jsonify({"nodes": [], "edges": []})

    with open(HEAD_PATH, "r") as f:
        curr = f.read().strip()

    nodes = []
    edges = []
    y_pos = 0

    while curr:
        obj_type, data = read_object(curr)
        lines = data.decode().splitlines()
        parent = None
        msg = ""
        for i, line in enumerate(lines):
            if line.startswith("parent "):
                parent = line.split(" ")[1]
            if line == "":
                msg = "\n".join(lines[i+1:])
                break

        nodes.append({
            "id": curr,
            "position": {"x": 300, "y": y_pos},
            "data": {"label": f"{curr[:7]}\n{msg}"},
            "style": {
                "backgroundColor": "#fff", 
                "border": "2px solid #2563eb", 
                "borderRadius": "8px", 
                "padding": "15px", 
                "fontWeight": "bold",
                "fontFamily": "sans-serif"
            }
        })

        if parent:
            edges.append({
                "id": f"e-{parent}-{curr}",
                "source": parent,
                "target": curr,
                "animated": True,
                "style": {"stroke": "#2563eb", "strokeWidth": 2}
            })
            curr = parent
            y_pos += 120
        else:
            curr = None

    return jsonify({"nodes": nodes, "edges": edges})

if __name__ == '__main__':
    app.run(port=5001)