# Archived: Janavani CLI Installation Guidelines

This document is preserved as historical planning material.

It described a proposed `janavani-cli` Cargo package, website copy-to-terminal integration, and a release workflow for CLI binaries. The current root `Cargo.toml` defines the package as `janavani`, not `janavani-cli`, and the current repository does not contain a standalone CLI package or the proposed CLI release workflow.

Do not treat this document as a current implementation contract. If a Janavani CLI is introduced later, it must be designed as a shared capability/client surface against the canonical ecosystem contracts rather than as a separate source of business logic.

---

Historical source content is retained below.

# Developer Guidelines: Automating CLI Distribution & Web Integration

## 1. Web Integration: Interactive Copy-to-Terminal Component
To allow users to opt-in and easily copy the installation commands, add an interactive element to the website.

### Step 1.1: Add the HTML Markup
```html
<div class="cli-install-container" style="border: 1px solid #ccc; padding: 20px; border-radius: 8px; margin: 20px 0;">
    <h3>🛠️ Install Janavani CLI Tooling (Opt-In)</h3>
    <p>Open your local terminal and run the development tool components via Cargo:</p>
    <div style="background: #f4f4f4; padding: 10px; border-radius: 4px; display: flex; justify-content: space-between; align-items: center;">
        <code id="cargoCommand">cargo install janavani-cli</code>
        <button onclick="copyCargoCommand()">📋 Copy</button>
    </div>
</div>
```

### Step 1.2: Add the JavaScript Functionality
```javascript
function copyCargoCommand() {
    const commandText = document.getElementById("cargoCommand").innerText;
    navigator.clipboard.writeText(commandText)
        .then(() => alert("Command copied to clipboard! Paste it into your terminal to install."))
        .catch(err => console.error("Failed to copy command: ", err));
}
```

## 2. Cargo Package Optimization
The historical proposal expected a Cargo package named `janavani-cli`.

## 3. CI/CD: Automated Multi-Platform Binary Releases
The historical proposal described a tag-triggered multi-platform binary release workflow.

## 4. Maintenance and Best Practices
The historical proposal recommended SemVer tags and local parsing/credential handling for a future CLI.
