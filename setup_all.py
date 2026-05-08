#!/usr/bin/env python3
"""
Build llama-server from source and install it alongside the other services.
"""
import subprocess, os, sys, shutil
from pathlib import Path

WORKSPACE = Path("/root/.openclaw-zhx/workspace")
PROJECT_DIR = WORKSPACE / "projects" / "genshin-knowledge"
LLAMA_DIR = PROJECT_DIR / "llama.cpp"
LLAMA_SERVER = LLAMA_DIR / "build" / "bin" / "llama-server"
MODEL_PATH = Path("/root/.node-llama-cpp/models/hf_ggml-org_embeddinggemma-300m-qat-Q8_0.gguf")

def step(msg):
    print(f"\n{'='*60}")
    print(f"  {msg}")
    print('='*60)

# Step 1: Build llama-server
step("1/4: Building llama-server from source")
if LLAMA_SERVER.exists():
    print("✅ Already built")
else:
    if not (LLAMA_DIR / "CMakeLists.txt").exists():
        subprocess.run([
            "git", "clone", "--depth=1",
            "https://github.com/ggml-org/llama.cpp.git",
            str(LLAMA_DIR),
        ], check=True)
    os.makedirs(LLAMA_DIR / "build", exist_ok=True)
    subprocess.run([
        "cmake", "-B", "build",
        "-DLLAMA_BUILD_SERVER=ON",
        "-DLLAMA_CUDA=OFF",  # CPU-only for embedding
        "-DCMAKE_BUILD_TYPE=Release",
    ], cwd=LLAMA_DIR, check=True)
    subprocess.run(["cmake", "--build", "build", "--config", "Release", "-j", "4"],
                   cwd=LLAMA_DIR, check=True)
    print("✅ llama-server built")

# Step 2: Start Qdrant
step("2/4: Starting Qdrant")
r = subprocess.run(["docker", "ps", "--filter", "name=qdrant", "--format", "{{.Names}}"],
                    capture_output=True, text=True)
if "qdrant" in r.stdout:
    print("✅ Qdrant already running")
else:
    subprocess.run(["docker", "run", "-d", "--name", "qdrant",
                    "-p", "6333:6333", "-p", "6334:6334",
                    "qdrant/qdrant"], check=True)
    print("✅ Qdrant started")

# Step 3: Start llama-server
step("3/4: Starting llama-server (embedding model)")
r = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True)
if ":8080" in r.stdout:
    print("✅ llama-server already running on :8080")
else:
    subprocess.Popen([
        str(LLAMA_SERVER),
        "-m", str(MODEL_PATH),
        "--port", "8080",
        "--embedding",
        "--n-gpu-layers", "0",
        "--ctx-size", "2048",
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("⏳ llama-server starting...")

# Step 4: Start search service
step("4/4: Starting Genshin Search Service")
r = subprocess.run(["ss", "-tlnp"], capture_output=True, text=True)
if ":8090" in r.stdout:
    print("✅ genshin-search already running on :8090")
else:
    subprocess.Popen([
        sys.executable, str(PROJECT_DIR / "genshin_search_service.py"),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("⏳ genshin-search starting...")

print(f"\n{'='*60}")
print("  All services starting. Check status with:")
print(f"  curl http://localhost:8090/health")
print(f"{'='*60}")
