# Graphify — Local Codebase Intelligence Workflow

**Purpose:** Help engineers and coding assistants navigate the existing JanaVani codebase and estimate change impact without repeatedly scanning the whole repository.

**Status:** Developer-tooling guidance; not a JanaVani runtime dependency and not a citizen-facing capability.

## 1. Operating boundary

Use Graphify as a local, derived map of code relationships. GitHub source, reviewed architecture documents, tests, CI and production evidence remain authoritative.

Graphify does not prove that a workflow works, that an authorization boundary is secure, or that a capability is production-ready. A graph edge may be inferred; inspect the underlying source and test before relying on it.

The first rollout is deliberately **code-only and local**:
- Tree-sitter parses supported code and configuration structures locally.
- The code-only extraction path requires no API key and does not send code to an LLM.
- Do not run semantic extraction over the full repository by default. Documentation, PDFs, images and transcripts can enter a model-processing pass; only add curated, approved material later.

## 2. Install and build the local graph

Use Python 3.11.5–3.14 and uv or pipx. Graphify's official package is <code>graphifyy</code> (two trailing y characters); the CLI command is <code>graphify</code>.

Pin the validated release for repeatability:

~~~bash
uv tool install graphifyy==0.9.118
graphify --version
graphify extract . --code-only
~~~

The default output is local under <code>graphify-out/</code>:
- <code>graph.json</code> — queryable code relationship graph.
- <code>GRAPH_REPORT.md</code> — generated architecture summary.
- <code>graph.html</code> — interactive browser map.

The repository ignores these generated artifacts. Do not commit them. Re-run the same extraction command after meaningful source changes; Graphify fingerprints files and can reuse unchanged extraction results.

## 3. JanaVani query patterns

Use a focused question first, then inspect exact source files.

~~~bash
# Trace the shared Case composition and its storage/provider dependencies.
graphify query "How are WebApp and Telegram composed over the shared Case, Consent and Evidence capabilities?"

# Inspect the single drafting capability and review boundary.
graphify path "LetterDraftingCapability" "DocumentReviewCapability"
graphify explain "LetterDraftingCapability"

# Trace the webhook boundary into shared civic capabilities.
graphify query "How does Telegram webhook ingress reach the update inbox and shared civic Case workflow?"

# Inspect consent persistence and transaction ownership.
graphify path "ConsentCapability" "PostgresConsentCaseAtomicRepository"
graphify explain "PostgresConsentCaseAtomicRepository"

# Investigate provider and surface failure boundaries.
graphify query "Which modules compose PostgreSQL repositories for independent Web and Telegram surfaces?"
~~~

Use the graph to discover callers, dependencies, likely tests and ownership boundaries. Then:
1. Open the exact source and contract files.
2. Read the relevant tests and migrations.
3. Verify the actual diff and run the required tests/CI.
4. Update the graph after the change and compare the affected relationships.

Do not split code merely because Graphify shows a large or highly connected node. Split only at a real boundary of change, trust, persistence, provider dependency or independent reuse.

## 4. Optional local MCP server

For an MCP-capable coding assistant, install Graphify's local stdio extra and point it at the generated graph:

~~~bash
uv tool install "graphifyy[mcp]==0.9.118"
graphify-mcp graphify-out/graph.json
~~~

In an MCP client that supports stdio servers, the command/argument pair is:

~~~json
{
  "mcpServers": {
    "janavani-graph": {
      "command": "graphify-mcp",
      "args": ["graphify-out/graph.json"]
    }
  }
}
~~~

Keep this configuration in the developer's local client settings unless the team explicitly standardizes one assistant configuration. The graph itself remains local.

## 5. Hosted Graphify MCP is a different deployment

<code>Graphify-Labs/graphify-mcp</code> is the public connection/documentation repository for Graphify's hosted service; its README says the hosted server implementation is maintained privately. The documented endpoint is <code>https://api.graphify.com/mcp</code> with browser OAuth.

That hosted option is not the same as the local CLI/MCP package. It requires connecting and indexing a repository in a Graphify workspace and sends repository content to an external service. Do not connect JanaVani to the hosted service by default. Consider it only after an explicit data-residency, retention, access-control and contractual review.

## 6. Exclusion and privacy rules

The root <code>.graphifyignore</code> excludes:
- archived generations and archived documentation, which otherwise create duplicate symbols and misleading paths;
- environment files, credentials, private keys, database snapshots, uploads, user-data and local runtime directories;
- test fixtures, which may contain realistic personal details.

Review these exclusions whenever repository layout changes. If new sensitive-data directories are introduced, add them before rebuilding the graph.

## 7. Adoption gate

Start with one local code-only graph and use it for architecture navigation and review preparation. Do not add Graphify as:
- a production service or JanaVani capability;
- a dependency of WebApp, Telegram or other citizen surfaces;
- an authoritative policy, consent or security decision engine;
- a mandatory CI gate until graph generation is reproducible and its maintenance value is demonstrated.

**Acceptance:** an engineer can use a local graph to locate the canonical Case, drafting, consent, storage and webhook call paths, then verify each finding against source, tests and CI.