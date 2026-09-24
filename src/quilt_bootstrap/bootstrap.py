"""Bootstrap the Quilt fleet from GitHub."""
from __future__ import annotations
import os
import subprocess
import json
import time
from typing import Optional


# The fleet — ordered by importance for fresh sandbox restoration
FLEET: list[dict] = [
    {
        "name": "quilt-seed",
        "url": "https://github.com/SuperInstance/quilt-seed",
        "purpose": "Substrate + 14-tuple + 11 opcodes + Vessel + Legalese",
        "walker_count": 2,
        "deps": [],
    },
    {
        "name": "quilt-schema-registry",
        "url": "https://github.com/SuperInstance/quilt-schema-registry",
        "purpose": "Canonical envelope contract",
        "walker_count": 1,
        "deps": [],
    },
    {
        "name": "quilt-trace",
        "url": "https://github.com/SuperInstance/quilt-trace",
        "purpose": "Witness chain visualizer",
        "walker_count": 1,
        "deps": [],
    },
    {
        "name": "quilt-organism",
        "url": "https://github.com/SuperInstance/quilt-organism",
        "purpose": "Corpus walker with multi-receiver composition",
        "walker_count": 2,
        "deps": [],
    },
    {
        "name": "quilt-optimization",
        "url": "https://github.com/SuperInstance/quilt-optimization",
        "purpose": "NVIDIA cuOpt substrate (VRP + LP/MILP)",
        "walker_count": 2,
        "deps": [],
    },
    {
        "name": "quilt-director",
        "url": "https://github.com/SuperInstance/quilt-director",
        "purpose": "Spiral knowledge builder + landing pages",
        "walker_count": 1,
        "deps": ["quilt-seed"],
    },
    {
        "name": "quilt-fleet-snapshot",
        "url": "https://github.com/SuperInstance/quilt-fleet-snapshot",
        "purpose": "Bake the fleet into a portable tarball",
        "walker_count": 1,
        "deps": [],
    },
    {
        "name": "quilt-brewer",
        "url": "https://github.com/SuperInstance/quilt-brewer",
        "purpose": "Grow new walkers from recipes (the recursion)",
        "walker_count": 1,
        "deps": ["quilt-schema-registry"],
    },
    {
        "name": "quilt-perception",
        "url": "https://github.com/SuperInstance/quilt-perception",
        "purpose": "Sensor stream routing (first walker brewed by the brewer)",
        "walker_count": 1,
        "deps": [],
    },
    {
        "name": "quilt-canon-witness",
        "url": "https://github.com/SuperInstance/quilt-canon-witness",
        "purpose": "Append-only cryptographic witness log (ledger substrate)",
        "walker_count": 1,
        "deps": [],
    },
    {
        "name": "quilt-fable",
        "url": "https://github.com/SuperInstance/quilt-fable",
        "purpose": "Multi-voice narrative substrate walker (brewed)",
        "walker_count": 1,
        "deps": [],
    },
    {
        "name": "quilt-orchestrator",
        "url": "https://github.com/SuperInstance/quilt-orchestrator",
        "purpose": "DAG-based composer substrate walker (brewed)",
        "walker_count": 1,
        "deps": [],
    },
    {
        "name": "quilt-linker",
        "url": "https://github.com/SuperInstance/quilt-linker",
        "purpose": "Substrate-to-substrate graph linker (brewed)",
        "walker_count": 1,
        "deps": [],
    },
]


# Modes — what to install
MODES = {
    "minimal": [
        "quilt-seed",
        "quilt-schema-registry",
        "quilt-trace",
        "quilt-organism",
        "quilt-canon-witness",
    ],
    "full": [r["name"] for r in FLEET],
    "demo": [
        "quilt-seed",
        "quilt-schema-registry",
        "quilt-trace",
        "quilt-brewer",
        "quilt-director",
        "quilt-perception",
        "quilt-fable",
    ],
}


# Linked walker instances per repo
LINKED_WALKERS = {
    "quilt-seed": ["vibe", "cu_substrate"],
    "quilt-organism": ["substrate", "scouts"],
    "quilt-trace": ["renderer"],
    "quilt-optimization": ["routing", "linear_programming"],
    "quilt-fleet-snapshot": ["snapshot"],
    "quilt-schema-registry": ["registry"],
    "quilt-brewer": ["brewer"],
    "quilt-perception": ["sensor_stream"],
    "quilt-canon-witness": ["ledger"],
    "quilt-fable": ["narrative"],
    "quilt-orchestrator": ["dag"],
    "quilt-linker": ["graph"],
    "quilt-director": ["spirals"],
}


def check_status(prefix: str = "/workspace") -> dict:
    """Check which fleet repos are installed and what their status is."""
    status = {
        "prefix": prefix,
        "repos": [],
        "missing": [],
        "outdated": [],
        "walker_count": 0,
        "total_size_bytes": 0,
    }

    for repo in FLEET:
        path = os.path.join(prefix, "repos", repo["name"])
        if os.path.exists(path):
            size = sum(
                os.path.getsize(os.path.join(d, f))
                for d, _, fs in os.walk(path)
                if not any(skip in d for skip in [".git", "__pycache__", "node_modules"])
                for f in fs
            )
            # Try to get git hash
            head = _git_head(path)
            status["repos"].append({
                "name": repo["name"],
                "present": True,
                "size_bytes": size,
                "head": head,
                "purpose": repo["purpose"],
                "walker_count": repo["walker_count"],
            })
            status["walker_count"] += repo["walker_count"]
            status["total_size_bytes"] += size
        else:
            status["repos"].append({
                "name": repo["name"],
                "present": False,
                "purpose": repo["purpose"],
            })
            status["missing"].append(repo["name"])

    return status


def bootstrap(mode: str = "minimal", prefix: str = "/workspace",
              shallow: bool = True,
              verbose: bool = True,
              run_tests: bool = False) -> dict:
    """Bootstrap the Quilt fleet.

    Args:
        mode: "minimal" | "full" | "demo" — what to install
        prefix: where to install (default /workspace)
        shallow: use shallow clones (faster)
        verbose: print progress
        run_tests: run each repo's tests after install

    Returns:
        {
            "ok": bool,
            "mode": mode,
            "cloned": list[str],
            "skipped": list[str],
            "errors": list[str],
            "total_walker_count": int,
            "elapsed_sec": float,
        }
    """
    if mode not in MODES:
        return {"ok": False, "error": f"unknown mode: {mode}",
                "available_modes": list(MODES.keys())}

    wanted = set(MODES[mode])
    cloned = []
    skipped = []
    errors = []
    walker_count = 0
    start = time.time()

    if verbose:
        print(f"\n🌱 Bootstrapping Quilt fleet — mode={mode} prefix={prefix}")
        print(f"   Want: {len(wanted)} repos")

    repos_dir = os.path.join(prefix, "repos")
    os.makedirs(repos_dir, exist_ok=True)

    for repo in FLEET:
        if repo["name"] not in wanted:
            continue

        target = os.path.join(repos_dir, repo["name"])

        if os.path.exists(target):
            skipped.append(repo["name"])
            walker_count += repo["walker_count"]
            if verbose:
                print(f"  ⏭  {repo['name']} already present")
            continue

        # Clone
        cmd = ["git", "clone"]
        if shallow:
            cmd.extend(["--depth", "1"])
        cmd.extend([repo["url"], target])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if result.returncode != 0:
                errors.append(f"{repo['name']}: {result.stderr.strip()[:100]}")
                if verbose:
                    print(f"  ✗ {repo['name']}: {result.stderr.strip()[:100]}")
                continue
            cloned.append(repo["name"])
            walker_count += repo["walker_count"]
            if verbose:
                print(f"  ✓ {repo['name']} cloned ({repo['walker_count']} walkers)")
        except Exception as e:
            errors.append(f"{repo['name']}: {e}")
            if verbose:
                print(f"  ✗ {repo['name']}: {e}")

        # Run tests if requested
        if run_tests and os.path.exists(os.path.join(target, "tests")):
            try:
                result = subprocess.run(
                    ["python3", "-m", "unittest", "discover", "-s", "tests",
                     "-p", "test_*.py"],
                    cwd=target, capture_output=True, text=True, timeout=30,
                )
                if verbose:
                    if result.returncode == 0:
                        print(f"    └ tests pass")
                    else:
                        print(f"    └ tests FAILED")
            except Exception:
                pass

    elapsed = time.time() - start

    if verbose:
        print(f"\n  Cloned: {len(cloned)} | Skipped: {len(skipped)} | Errors: {len(errors)}")
        print(f"  Total walker instances: {walker_count}")
        print(f"  Elapsed: {elapsed:.1f}s")

    return {
        "ok": len(errors) == 0,
        "mode": mode,
        "cloned": cloned,
        "skipped": skipped,
        "errors": errors,
        "total_walker_count": walker_count,
        "elapsed_sec": elapsed,
    }


def _git_head(repo_dir: str) -> Optional[str]:
    """Get short hash of HEAD."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_dir, "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except Exception:
        return None
