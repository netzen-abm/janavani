                                 [ JANAVANI V3 ISOMORPHIC CLIENT ]
                                  (Android / iOS / WebAssembly SPA)
                                                 │
                 ┌───────────────────────────────┼───────────────────────────────┐
                 ▼ (If Net Available)            ▼ (If Net Compromised)          ▼ (If Net Down)
          [ Nym Mixnet Proxy ]           [ TLS 1.3 mTLS Proxy ]         [ Reticulum Mesh Node ]
                 │                               │                              │
                 └───────────────────────────────┼──────────────────────────────┘
                                                 ▼
                                   [ Secure NGINX Gateway (443) ]
                                                 │
                                  (Internal Bridge / Port 8000)
                                                 ▼
                                  [ FastAPI Ingestion Core Container ]
                                                 │
                        ┌────────────────────────┴────────────────────────┐
                        ▼                                                 ▼
         [ Celery Ingestion Worker ]                       [ Air-Gapped Ollama Sandbox ]
                        │                                        (Local Llama-3-8B SLM)
                        ▼
         [ In-Memory Redis Mesh ]
       (No Persistent Disk Storage)


Janavani V3 operates as an Isomorphic Single-Page Application (SPA) written in Rust (Dioxus). 
It compiles natively to an Android APK, an iOS App bundle, and a WebAssembly (WASM) binary [source 5]. 
It contains no standard relational database pipelines.All analytics and temporary generation codes are held in a volatile, in-memory Redis cluster running inside an air-gapped Docker network sandbox with disk-writing explicitly deactivated [source 1].
