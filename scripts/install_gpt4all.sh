#!/usr/bin/env bash
# scripts/install_gpt4all.sh
# Helper script: install gpt4all Python package into the active virtualenv and print next steps.
set -e

if [ -z "$VIRTUAL_ENV" ]; then
  echo "Warning: no active Python virtualenv detected. It's recommended to create one first:"
  echo "  python3 -m venv .venv && source .venv/bin/activate"
fi

echo "Installing gpt4all Python package (will install into active venv)..."
python -m pip install --upgrade pip
python -m pip install gpt4all

cat <<'EOF'

Installed gpt4all Python package.
Next steps (manual):
1) Download a GPT4All-compatible model (ggml/gguf/.bin) from the GPT4All releases or Hugging Face and place the file in ./models/
   Example model filenames: gpt4all-l13b-snoozy.bin or a .gguf file.
2) Run the example runner:
   python scripts/run_gpt4all_example.py

See docs/GPT4ALL.md for detailed guidance.
EOF
