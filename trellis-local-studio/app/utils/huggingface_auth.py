"""Hugging Face authentication helpers for gated TRELLIS.2 dependencies."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

# Models loaded by Trellis2ImageTo3DPipeline.from_pretrained("microsoft/TRELLIS.2-4B").
REQUIRED_HF_REPOS = (
    {
        "repo_id": "microsoft/TRELLIS.2-4B",
        "label": "TRELLIS.2 main model",
        "access_url": "https://huggingface.co/microsoft/TRELLIS.2-4B",
        "gated": False,
        "probe_file": "pipeline.json",
    },
    {
        "repo_id": "facebook/dinov3-vitl16-pretrain-lvd1689m",
        "label": "DINOv3 image encoder",
        "access_url": "https://huggingface.co/facebook/dinov3-vitl16-pretrain-lvd1689m",
        "gated": True,
        "probe_file": "config.json",
    },
    {
        "repo_id": "briaai/RMBG-2.0",
        "label": "Background removal model (BiRefNet / RMBG-2.0)",
        "access_url": "https://huggingface.co/briaai/RMBG-2.0",
        "gated": True,
        "probe_file": "config.json",
    },
)

GATED_REPO_URLS = tuple(repo["access_url"] for repo in REQUIRED_HF_REPOS if repo["gated"])


@dataclass(frozen=True)
class HuggingFaceAuthStatus:
    logged_in: bool
    username: str | None
    repos: list[dict[str, Any]]
    error: str | None = None

    @property
    def ready(self) -> bool:
        return self.logged_in and all(repo.get("accessible") for repo in self.repos)

    @property
    def blocked_repos(self) -> list[dict[str, Any]]:
        return [repo for repo in self.repos if not repo.get("accessible")]


def _probe_repo_access(repo_id: str, probe_file: str) -> None:
    from huggingface_hub import hf_hub_download

    hf_hub_download(repo_id, probe_file)


def check_huggingface_auth() -> HuggingFaceAuthStatus:
    """Return login state and whether required model repos are accessible."""

    try:
        from huggingface_hub import HfApi
        from huggingface_hub.utils import GatedRepoError, HfHubHTTPError
    except Exception as exc:
        return HuggingFaceAuthStatus(
            logged_in=False,
            username=None,
            repos=[],
            error=f"huggingface_hub is not available: {exc}",
        )

    api = HfApi()
    username: str | None = None
    try:
        whoami = api.whoami()
        username = whoami.get("name") or whoami.get("fullname")
        logged_in = True
    except Exception:
        logged_in = False

    repo_status: list[dict[str, Any]] = []
    for repo in REQUIRED_HF_REPOS:
        entry = {
            "repo_id": repo["repo_id"],
            "label": repo["label"],
            "access_url": repo["access_url"],
            "gated": repo["gated"],
            "accessible": False,
            "error": None,
        }
        if not logged_in:
            entry["error"] = "Not logged in to Hugging Face."
            repo_status.append(entry)
            continue
        try:
            _probe_repo_access(repo["repo_id"], repo["probe_file"])
            entry["accessible"] = True
        except GatedRepoError:
            entry["error"] = "Access not granted yet. Open the model page and accept the license."
        except HfHubHTTPError as exc:
            if exc.response.status_code in {401, 403}:
                entry["error"] = "Access not granted yet. Open the model page and accept the license."
            else:
                entry["error"] = str(exc)
        except Exception as exc:
            entry["error"] = str(exc)
        repo_status.append(entry)

    return HuggingFaceAuthStatus(logged_in=logged_in, username=username, repos=repo_status)


def format_huggingface_setup_help(blocked: list[dict[str, Any]] | None = None) -> str:
    """Human-readable setup steps for gated Hugging Face models."""

    lines = [
        "Hugging Face login and gated-model access are required for TRELLIS.2.",
        "",
        "1. Create or sign in: https://huggingface.co/join",
        "2. Request access to each gated model below and accept the license:",
    ]
    targets = blocked or [repo for repo in REQUIRED_HF_REPOS if repo["gated"]]
    if not targets:
        targets = [repo for repo in REQUIRED_HF_REPOS if repo["gated"]]
    for repo in targets:
        lines.append(f"   - {repo['repo_id']}: {repo['access_url']}")
    lines.extend(
        [
            "3. Create a read token: https://huggingface.co/settings/tokens",
            "4. Log in on this machine:",
            "   cd trellis-local-studio",
            "   source \"$HOME/miniforge3/etc/profile.d/conda.sh\"",
            "   conda activate trellis2",
            "   hf auth login",
            "5. Verify access:",
            "   ./scripts/setup_huggingface.sh --check --download",
            "6. Restart the app:",
            "   ./scripts/stop_app.sh && ./scripts/run_app.sh",
            "",
            "Then retry generation.",
        ]
    )
    return "\n".join(lines)


def _repo_from_error(raw_message: str) -> str | None:
    match = re.search(r"huggingface\.co/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+)", raw_message)
    if match:
        return match.group(1)
    for repo in REQUIRED_HF_REPOS:
        if repo["repo_id"] in raw_message:
            return repo["repo_id"]
    return None


def gated_repo_error_message(raw_message: str) -> str | None:
    """Return a friendly message when Hugging Face rejects a gated repo."""

    lowered = raw_message.lower()
    if (
        "gated repo" not in lowered
        and "restricted" not in lowered
        and "please log in" not in lowered
        and "authorized list" not in lowered
        and "403 client error" not in lowered
    ):
        return None

    repo_id = _repo_from_error(raw_message)
    repo_hint = ""
    if repo_id:
        access_url = next(
            (repo["access_url"] for repo in REQUIRED_HF_REPOS if repo["repo_id"] == repo_id),
            f"https://huggingface.co/{repo_id}",
        )
        repo_hint = f"\nBlocked repo: {repo_id}\nAccept access at: {access_url}"

    status = check_huggingface_auth()
    blocked = status.blocked_repos
    return (
        "Hugging Face authentication or gated-model access is missing."
        f"{repo_hint}\n\n{format_huggingface_setup_help(blocked if blocked else None)}"
    )
