# CLAUDE.md — Claude Code Instructions

This project uses `AGENTS.md` as the canonical build specification.

Before making changes, read and follow:

- `AGENTS.md`
- `README.md`
- `docs/BUILD_PROCESS.md`
- `docs/FUNCTIONALITY.md`
- `docs/USER_GUIDE.md`
- `docs/TROUBLESHOOTING.md`
- `docs/ARCHITECTURE.md`
- `docs/CHANGELOG.md`

The app goal is a standalone Ubuntu Desktop visual application for local TRELLIS.2 image-to-3D generation on an RTX 3090.

Important constraints:

- Image-to-3D only
- No integrated image creation
- No text-to-image
- No ComfyUI dependency
- Local-only by default
- Proper visual interface required
- Documentation must be updated during the build
- TRELLIS.2 is single-image based unless a verified multi-view module is later implemented

When implementing features, keep documentation updated in the same session as code changes.
