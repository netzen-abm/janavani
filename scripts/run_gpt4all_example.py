#!/usr/bin/env python3
# scripts/run_gpt4all_example.py
# Minimal example that attempts to run a local GPT4All model found in ./models/

import os
import sys

MODEL_DIR = "models"

def find_model():
    if not os.path.isdir(MODEL_DIR):
        return None
    for fname in os.listdir(MODEL_DIR):
        if fname.lower().endswith(('.bin', '.gguf', '.ggml', '.bin.gz')):
            return os.path.join(MODEL_DIR, fname)
    return None

if __name__ == '__main__':
    model_path = find_model()
    if model_path is None:
        print("No GPT4All-compatible model found in ./models/.")
        print("Please download a model (e.g., gpt4all-l13b-snoozy.bin) and place it in the models/ directory.")
        print("See docs/GPT4ALL.md for guidance on where to get models and how to set up the runtime.")
        sys.exit(1)

    try:
        from gpt4all import GPT4All
    except Exception as e:
        print("Could not import gpt4all Python package. Please install it (see scripts/install_gpt4all.sh).\n", e)
        sys.exit(1)

    print(f"Using model: {model_path}")
    # Instantiate the model (best-effort; API may vary by gpt4all version)
    try:
        # Some gpt4all versions accept a model name string or a path. We pass the path.
        gpt = GPT4All(model=model_path)

        prompt = (
            "You are an assistant that drafts a formal legal complaint letter (India context).\n"
            "Draft a concise 4-6 sentence complaint about water supply being cut for two months."
        )

        print("\nPrompt:\n", prompt)
        print("\nGenerating... (this may take a while on CPU)")

        # generate() can return a string or a generator depending on package version; guard accordingly
        try:
            out = gpt.generate(prompt)
            # If generate returns a dict or list, try to extract text
            if isinstance(out, (list, tuple)):
                print('\n'.join([str(x) for x in out]))
            else:
                print(out)
        except TypeError:
            # Fallback: some versions use a .chat or .completion interface
            try:
                out = gpt.chat(prompt)
                print(out)
            except Exception:
                print("Generation call failed. Check gpt4all package version and API. See docs/GPT4ALL.md.")
    except Exception as e:
        print("Failed to initialize or run the GPT4All model:", e)
        print("If you have a different runtime (llama.cpp, ggml, or a model server), follow docs/GPT4ALL.md for instructions.")
        sys.exit(1)
