"""Tests for quilt-bootstrap."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from quilt_bootstrap import (
    bootstrap, check_status, MODES, FLEET, LINKED_WALKERS, __version__,
)


class TestBootstrapMetadata(unittest.TestCase):
    def test_version(self):
        self.assertEqual(__version__, "0.1.0")

    def test_fleet_is_a_list(self):
        self.assertIsInstance(FLEET, list)
        self.assertGreaterEqual(len(FLEET), 7)

    def test_each_fleet_repo_has_required_keys(self):
        for repo in FLEET:
            for k in ["name", "url", "purpose", "walker_count", "deps"]:
                self.assertIn(k, repo, f"{repo.get('name', '?')} missing {k}")

    def test_fleet_repos_have_urls(self):
        for repo in FLEET:
            self.assertTrue(repo["url"].startswith("https://github.com/"),
                            f"{repo['name']} bad URL")
            self.assertIn("SuperInstance/", repo["url"])

    def test_modes_dict(self):
        self.assertIsInstance(MODES, dict)
        self.assertIn("minimal", MODES)
        self.assertIn("full", MODES)
        self.assertIn("demo", MODES)
        self.assertEqual(set(MODES["full"]), set(r["name"] for r in FLEET))

    def test_linked_walkers_covers_all(self):
        for repo in FLEET:
            self.assertIn(repo["name"], LINKED_WALKERS,
                          f"no linked walker for {repo['name']}")

    def test_linked_walker_count_matches(self):
        """LINKED_WALKERS count must equal walker_count in FLEET."""
        for repo in FLEET:
            linked = len(LINKED_WALKERS.get(repo["name"], []))
            self.assertEqual(linked, repo["walker_count"],
                             f"{repo['name']}: linked={linked} vs declared={repo['walker_count']}")


class TestBootstrap(unittest.TestCase):
    def test_unknown_mode_returns_error(self):
        result = bootstrap(mode="does-not-exist", prefix="/tmp", verbose=False)
        self.assertFalse(result["ok"])
        self.assertIn("unknown mode", result["error"])

    def test_minimal_mode_runs(self):
        with tempfile.TemporaryDirectory() as dest:
            result = bootstrap(mode="minimal", prefix=dest, verbose=False)
            # Should not error
            self.assertNotIn("error", result, f"got error key: {result}")
            # Should be ok or have errors only if clone fails (network)
            self.assertIn("ok", result)

    def test_check_status_returns_expected_keys(self):
        with tempfile.TemporaryDirectory() as dest:
            status = check_status(prefix=dest)
            for k in ["prefix", "repos", "missing", "walker_count", "total_size_bytes"]:
                self.assertIn(k, status)

    def test_check_status_includes_all_fleet_repos(self):
        with tempfile.TemporaryDirectory() as dest:
            status = check_status(prefix=dest)
            names = [r["name"] for r in status["repos"]]
            for repo in FLEET:
                self.assertIn(repo["name"], names, f"missing {repo['name']} in status")

    def test_check_status_marks_missing(self):
        with tempfile.TemporaryDirectory() as dest:
            status = check_status(prefix=dest)
            self.assertGreater(len(status["missing"]), 0)

    def test_check_status_with_existing_repo(self):
        with tempfile.TemporaryDirectory() as dest:
            # Create a fake repo dir
            fake = os.path.join(dest, "repos", "quilt-seed")
            os.makedirs(fake, exist_ok=True)
            with open(os.path.join(fake, "README.md"), "w") as f:
                f.write("test")
            status = check_status(prefix=dest)
            quilt_seed = next(r for r in status["repos"] if r["name"] == "quilt-seed")
            self.assertTrue(quilt_seed["present"])


class TestFleetInventory(unittest.TestCase):
    """The fleet inventory is the contract. Verify it's complete."""

    def test_walker_count_total(self):
        total = sum(repo["walker_count"] for repo in FLEET)
        self.assertGreaterEqual(total, 10)

    def test_no_duplicate_repos(self):
        names = [r["name"] for r in FLEET]
        self.assertEqual(len(names), len(set(names)))

    def test_deps_exist(self):
        all_names = {r["name"] for r in FLEET}
        for repo in FLEET:
            for dep in repo["deps"]:
                self.assertIn(dep, all_names, f"{repo['name']} depends on missing {dep}")


if __name__ == "__main__":
    unittest.main()
