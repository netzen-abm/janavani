# Environment Contract

## Provider credentials

Use canonical environment names across code, CI, and deployment:

- `OPENROUTER_API_KEY`
- `HF_TOKEN`
- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `TELEGRAM_BOT_TOKEN`

`HF_TOKEN` is the canonical Hugging Face credential name.
Do not introduce `HUGGINGFACE_API_KEY` as an alternate name.

## Design rule

Provider credentials belong to the runtime environment.
Capability code must consume configuration, not own credentials.

Tests use non-secret mock values.
Production credentials remain in the secret store.
