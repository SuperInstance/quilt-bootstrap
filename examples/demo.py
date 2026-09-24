"""quilt-bootstrap demo — show how a fresh sandbox boots the fleet."""
import os
import sys
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from quilt_bootstrap import bootstrap, check_status, MODES, FLEET


def main():
    print("\n" + "=" * 60)
    print("🌱 quilt-bootstrap demo")
    print("=" * 60)

    print(f"\n[Fleet inventory: {len(FLEET)} repos]")
    for repo in FLEET:
        deps = ", ".join(repo["deps"]) if repo["deps"] else "—"
        print(f"  • {repo['name']:25}  walkers={repo['walker_count']}  deps={deps}")
        print(f"    {repo['purpose']}")

    print(f"\n[Available modes]")
    for mode, repos in MODES.items():
        print(f"  • {mode:10} → {len(repos)} repos")

    # Check current status
    print(f"\n[Current status at /workspace]")
    status = check_status("/workspace")
    print(f"  Walker instances: {status['walker_count']}")
    print(f"  Total size: {status['total_size_bytes'] / 1024:.1f} KB")
    print(f"  Missing: {len(status['missing'])} repos")

    # Show what would happen in a fresh sandbox
    print(f"\n[Simulation: fresh sandbox with 'minimal' mode]")
    with tempfile.TemporaryDirectory() as dest:
        result = bootstrap(mode="minimal", prefix=dest, verbose=False)
        if result["ok"]:
            print(f"  ✓ Would install {len(result['cloned']) + len(result['skipped'])} repos")
            print(f"  ✓ {result['total_walker_count']} walker instances")
            print(f"  ✓ Elapsed: {result['elapsed_sec']:.1f}s")
        else:
            print(f"  ✗ Errors: {result['errors']}")

    print("\n" + "=" * 60)
    print("✅ Demo complete — bootstrap is one command away")
    print("=" * 60)


if __name__ == "__main__":
    main()
