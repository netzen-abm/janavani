# GPT4All integration notes

This doc explains how to run a CPU-local GPT4All model for quick, private testing of the generation step in the POC.

Requirements
- Python 3.9+
- A GPT4All-compatible model file (ggml/gguf/.bin). These are not included in this repo due to size and licensing.

Quick steps
1) Create and activate a virtualenv (recommended):
   python3 -m venv .venv
   source .venv/bin/activate

2) Install the Python client (this repo provides a helper script):
   bash scripts/install_gpt4all.sh

3) Download a GPT4All model (for CPU). Where to find models:
- GPT4All releases (official): search "GPT4All models" or visit the GPT4All project page.
- Hugging Face: some repo owners host ggml/gguf builds for local use.

4) Place the model file in the repo under ./models/ (create the directory if missing).
   Example file names: gpt4all-l13b-snoozy.bin or model.gguf

5) Run the example generator script:
   python scripts/run_gpt4all_example.py

Notes
- CPU generation can be slow for large models. For better performance use a smaller model or run on a machine with a dedicated GPU.
- The gpt4all Python API has varied across releases; the example runner uses a best-effort approach and prints helpful messages if the API differs.
- Check model license before using it in production.
