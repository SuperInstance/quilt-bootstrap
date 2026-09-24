# 🌱 quilt-bootstrap

> Bring up the Quilt fleet in a fresh sandbox. One command.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)]()
[![Tests](https://img.shields.io/badge/tests-16/16-brightgreen.svg)](tests/test_bootstrap.py)
[![Repos](https://img.shields.io/badge/fleet-9_repos-yellow.svg)]()
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

## What is this?

A single command clones, installs, and links every walker in the fleet.
Designed for use in fresh sandboxes (post-wipe restoration) or new
developer onboarding.

## The fleet (9 repos, 11 walker instances)

| Repo | Walkers | Purpose |
|---|---|---|
| `quilt-seed` | 2 | Substrate + 14-tuple + 11 opcodes + Vessel + Legalese |
| `quilt-schema-registry` | 1 | Canonical envelope contract |
| `quilt-trace` | 1 | Witness chain visualizer |
| `quilt-organism` | 2 | Corpus walker with multi-receiver composition |
| `quilt-optimization` | 2 | NVIDIA cuOpt substrate (VRP + LP/MILP) |
| `quilt-director` | 1 | Spiral knowledge builder + landing pages |
| `quilt-fleet-snapshot` | 1 | Bake the fleet into a portable tarball |
| `quilt-brewer` | 1 | Grow new walkers from recipes (the recursion) |
| `quilt-perception` | 1 | Sensor stream routing (first walker brewed) |

## Usage

### Check current status

```python
from quilt_bootstrap import check_status

status = check_status("/workspace")
print(f"Walker instances: {status['walker_count']}")
print(f"Total size: {status['total_size_bytes'] / 1024:.1f} KB")
print(f"Missing: {status['missing']}")
```

### Bootstrap a fresh sandbox

```python
from quilt_bootstrap import bootstrap

# Minimal — 4 repos, 6 walkers, ~30 seconds
result = bootstrap(mode="minimal", prefix="/workspace")
# Cloned: 4 repos, walker instances: 6, elapsed: ~30s

# Full — 9 repos, 11 walkers, ~90 seconds
result = bootstrap(mode="full", prefix="/workspace")

# Demo — 5 repos for the organism landing page
result = bootstrap(mode="demo", prefix="/workspace")
```

### CLI

```bash
python3 -m quilt_bootstrap [--mode {minimal,full,demo}] [--prefix /workspace]
```

## Modes

- **minimal**: just the core 4 repos (no GPU/visual stack)
- **full**: all 9 repos
- **demo**: just enough to run the organism landing page

## The wipe problem

After every fresh sandbox, the agent rebuilds the fleet from memory alone.
The bootstrap solves this by:

1. Cloning each repo from GitHub (shallow for speed)
2. Linking the walker instances to `LINKED_WALKERS`
3. Running tests (if `--run-tests` is set)
4. Reporting status

A fresh sandbox does:
```python
python3 -c "from quilt_bootstrap import bootstrap; bootstrap(mode='full')"
```

And the substrate walker pattern is online in <90 seconds, no rebuild needed.

## Why this matters

The substrate walker pattern has been re-derived ~11 times across the fleet.
The bootstrap codifies the fleet as a single command:

- No more "which version of which repo"
- No more "where do I clone to"
- No more "what depends on what"

The doctrine is now ship-able. The fleet is now a single pip-install.

## Related

- [quilt-fleet-snapshot](https://github.com/SuperInstance/quilt-fleet-snapshot) — bake the state
- [quilt-brewer](https://github.com/SuperInstance/quilt-brewer) — grow new walkers
- [quilt-schema-registry](https://github.com/SuperInstance/quilt-schema-registry) — validate
- [quilt-director](https://github.com/SuperInstance/quilt-director) — the spirals

## License

Apache-2.0
