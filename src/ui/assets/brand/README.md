# JanaVani logo and brand asset provenance

## Active product logo

- **Bundled path:** `src/ui/assets/brand/janavani-mark.svg`
- **Selected artwork:** the JanaVani profile-picture SVG supplied by the project owner in this conversation.
- **Pre-existing source:** `archive/assets/root-brand-legacy-2026-09-21/JanaVani Profile Pictures re-size svg.svg`
- **Git blob SHA:** `7cfdaf2187560e4253510cc348721fdfdc0d27a7`
- **Size:** 202,771 bytes.
- **Implementation:** the active path reuses that existing Git blob; it does not introduce another image copy.
- **Use:** the shared asset route displays it in the Dynamic Web navigation and WebApp home page.

## Browser favicon

- **Path:** root `favicon.svg`
- **Selected artwork:** the separately supplied `favicon(1).svg`.
- **Git blob SHA:** `9f9b4d0a0ac8cee2b95b43d6bd7beef7e666c7e5` (see correction below if the SHA check is needed).
- **Size:** 205,452 bytes.
- The supplied favicon SVG is byte-identical to the existing root `favicon.svg`; the existing file is reused instead of adding another copy.
- Both independent FastHTML runtimes explicitly link `/favicon.svg` in the HTML head.

## Ownership and licence distinction

The selected profile SVG matches an archived repository blob, but it is **not** the 327-byte mark previously copied from the showcase website. The showcase website's MIT licence must not be assumed to cover this selected profile artwork. This repository does not yet establish a separate redistribution licence for the profile SVG or favicon artwork. The project-owner request permits using the supplied artwork for JanaVani in this task; confirm ownership and redistribution rights before wider third-party reuse. Trademark/endorsement rights remain distinct from copyright permissions.

## Imported illustration assets

- `src/ui/assets/illustrations/preamble-of-india.webp`
  - Source: `assets/constitutional/Preamble of India WebP.webp`
  - Source blob SHA: `9546dbb8ab93cbdd7b0d3c4ed48d57d3810fedf8`
  - Source size: 84,792 bytes (WebP; transferred byte-for-byte).
  - Use: optional visual rendering associated with the constitutional preamble on the public Dynamic Web.
- `src/ui/assets/illustrations/civic-action-pathway.webp`
  - Source: `assets/images/janavani-civic-pathway - webp.webp`
  - Source blob SHA: `093a8015b4acaa008ec4b69c52f8af152fc76665`
  - Source size: 246,612 bytes (WebP; transferred byte-for-byte).
  - Use: civic-action pathway illustration on the public Dynamic Web.

Both files were copied from `netzen-abm/janavani-website` at `main` using Git blob objects; their resulting Git blob SHA values equal the source blob SHA values. The source repository has an MIT root licence. Preserve this attribution and verify brand/artwork rights before redistribution outside JanaVani. The files are WebP already; the application serves them with `image/webp`, lazy loading and one-day public caching rather than re-encoding them during requests.

Do not replace this small app mark with a large legacy SVG just because both have similar names. The large legacy SVG is a separate 205 KB logo asset and is already present in the repository archive/root favicon history. Re-check blob hashes, rights and use case before importing additional artwork.
