janavani/src/web_dioxus/
├── Cargo.toml              <-- Rust dependency configuration
├── Dioxus.toml             <-- Dioxus build tool configuration
└── src/
    ├── main.rs             <-- Entry point, SPA Router & UI Rendering Engine
    ├── api_client.rs       <-- Hybrid API driver (HTTPS Rest <-> Freenet Fetch)
    └── freenet_compat.rs   <-- Optional Freenet content addressable protocol hooks
