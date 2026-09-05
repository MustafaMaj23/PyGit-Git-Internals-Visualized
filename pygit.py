#!/usr/bin/env python3
import os
import sys
import hashlib
import zlib
import json
import time

PYGIT_DIR = ".pygit"
OBJECTS_DIR = os.path.join(PYGIT_DIR, "objects")
INDEX_PATH = os.path.join(PYGIT_DIR, "index")
HEAD_PATH = os.path.join(PYGIT_DIR, "HEAD")

def init():
    os.makedirs(OBJECTS_DIR, exist_ok=True)
    if not os.path.exists(INDEX_PATH):
        with open(INDEX_PATH, "w") as f:
            json.dump({}, f)
    if not os.path.exists(HEAD_PATH):
        with open(HEAD_PATH, "w") as f:
            f.write("")
    print("Initialized empty PyGit repository in .pygit/")

def hash_object(data: bytes, obj_type: str = "blob", write: bool = True) -> str:
    header = f"{obj_type} {len(data)}\0".encode()
    store = header + data
    sha1 = hashlib.sha1(store).hexdigest()
    
    if write:
        obj_dir = os.path.join(OBJECTS_DIR, sha1[:2])
        obj_file = os.path.join(obj_dir, sha1[2:])
        if not os.path.exists(obj_file):
            os.makedirs(obj_dir, exist_ok=True)
            with open(obj_file, "wb") as f:
                f.write(zlib.compress(store))
    return sha1

def read_object(sha1: str):
    obj_path = os.path.join(OBJECTS_DIR, sha1[:2], sha1[2:])
    if not os.path.exists(obj_path):
        raise FileNotFoundError(f"Object {sha1} not found")
    with open(obj_path, "rb") as f:
        raw = zlib.decompress(f.read())
    null_idx = raw.find(b"\0")
    header = raw[:null_idx].decode()
    obj_type, _ = header.split(" ")
    data = raw[null_idx + 1:]
    return obj_type, data

def add(filepath: str):
    if not os.path.exists(filepath):
        print(f"Error: file {filepath} does not exist.")
        return
    with open(filepath, "rb") as f:
        data = f.read()
    sha1 = hash_object(data, "blob", write=True)
    
    with open(INDEX_PATH, "r") as f:
        index = json.load(f)
    index[filepath] = sha1
    with open(INDEX_PATH, "w") as f:
        json.dump(index, f, indent=2)
    print(f"Staged {filepath} -> {sha1[:7]}")

def write_tree() -> str:
    with open(INDEX_PATH, "r") as f:
        index = json.load(f)
    
    tree_entries = []
    for filepath, sha1 in sorted(index.items()):
        tree_entries.append(f"100644 blob {sha1}\t{filepath}".encode())
    tree_data = b"\n".join(tree_entries)
    return hash_object(tree_data, "tree", write=True)

def commit(message: str):
    tree_sha = write_tree()
    parent = ""
    if os.path.exists(HEAD_PATH):
        with open(HEAD_PATH, "r") as f:
            parent = f.read().strip()
    
    timestamp = int(time.time())
    commit_payload = f"tree {tree_sha}\n"
    if parent:
        commit_payload += f"parent {parent}\n"
    commit_payload += f"author User <user@example.com> {timestamp}\n\n{message}\n"
    
    commit_sha = hash_object(commit_payload.encode(), "commit", write=True)
    with open(HEAD_PATH, "w") as f:
        f.write(commit_sha)
    print(f"[{commit_sha[:7]}] {message}")

def log_graph():
    if not os.path.exists(HEAD_PATH):
        print("No commits yet.")
        return
    with open(HEAD_PATH, "r") as f:
        curr = f.read().strip()

    while curr:
        _, data = read_object(curr)
        lines = data.decode().splitlines()
        parent = None
        msg = ""
        for i, line in enumerate(lines):
            if line.startswith("parent "):
                parent = line.split(" ")[1]
            if line == "":
                msg = "\n".join(lines[i+1:])
                break
        
        print(f"* Commit: {curr}")
        print(f"| Message: {msg}")
        if parent:
            print("|\n|")
        curr = parent

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: pygit.py <init|add|commit|log-graph> [args]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    if cmd == "init":
        init()
    elif cmd == "add" and len(sys.argv) > 2:
        add(sys.argv[2])
    elif cmd == "commit" and len(sys.argv) > 2:
        commit(sys.argv[2])
    elif cmd == "log-graph":
        log_graph()
    else:
        print("Invalid command or missing arguments.")