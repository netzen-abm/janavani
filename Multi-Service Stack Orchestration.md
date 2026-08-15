                        [ Public HTTP Requests (Port 8080) ]
                                         │
                                         ▼
                     ┌──────────────────────────────────────┐
                     │ Janavani FastHTML Frontend Container │
                     └───────────────────┬──────────────────┘
                                         │ (Internal Bridged API Calls)
                                         ▼
[ Public HTTPS (443) ] ──► [ NGINX Proxy Gateway ] ──► [ Python AI Agent Core ]


To run your new web frontend application automatically alongside your existing backend services, we can update your configuration to a Unified Multi-Container Topology Mesh.
This updates your infrastructure to run the FastHTML Web MVP application inside its own isolated frontend container container on Port 8080. This container communicates internally with your backend over the secure bridge network, ensuring a smooth and decoupled deployment.

