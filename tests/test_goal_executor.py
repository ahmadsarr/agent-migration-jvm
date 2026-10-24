import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from scripts.goal_executor import Blocked, complete, inspect


class GoalExecutorTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=Test", "-c",
                        "user.email=test@example.org", "commit", "-q", "--allow-empty", "-m", "init"], check=True)
        self.head = subprocess.check_output(["git", "-C", str(self.root), "rev-parse", "HEAD"], text=True).strip()
        self.branch = subprocess.check_output(["git", "-C", str(self.root), "branch", "--show-current"], text=True).strip()
        self.goal = {"id": "GOAL-001", "status": "VALIDATING", "dependencies": [],
                     "acceptance": [{"criterion": "inventory", "result": "PASS"}],
                     "report": "migration/reports/GOAL-001.md", "evidence": [],
                     "authorization": {"reportWrite": True}}
        self.state = {"schemaVersion": 1, "repository": {"head": self.head, "branch": self.branch},
                      "goals": [self.goal]}
        report = self.root / self.goal["report"]
        report.parent.mkdir(parents=True)
        report.write_text("# Inventory\n")

    def tearDown(self):
        self.tmp.cleanup()

    def test_completed_self_dependency_rejected(self):
        self.goal["status"] = "COMPLETED"
        self.goal["dependencies"] = ["GOAL-001"]
        with self.assertRaises(Blocked):
            inspect(self.root, self.state)

    def test_completed_cycle_rejected(self):
        self.goal["status"] = "COMPLETED"
        self.goal["dependencies"] = ["GOAL-002"]
        self.state["goals"].append(dict(self.goal, id="GOAL-002", dependencies=["GOAL-001"]))
        with self.assertRaises(Blocked):
            inspect(self.root, self.state)

    def test_success(self):
        self.assertTrue(complete(self.root, self.state, "GOAL-001"))
        self.assertEqual(self.goal["status"], "COMPLETED")
        inspect(self.root, self.state)

    def test_failed_check(self):
        self.goal["acceptance"][0]["result"] = "FAIL"
        with self.assertRaises(Blocked):
            complete(self.root, self.state, "GOAL-001")

    def test_missing_report(self):
        (self.root / self.goal["report"]).unlink()
        with self.assertRaises(Blocked):
            complete(self.root, self.state, "GOAL-001")

    def test_no_authorization(self):
        self.goal["authorization"]["reportWrite"] = False
        with self.assertRaises(Blocked):
            complete(self.root, self.state, "GOAL-001")

    def test_git_divergence(self):
        self.state["repository"]["head"] = "wrong"
        with self.assertRaises(Blocked):
            inspect(self.root, self.state)

    def test_path_escape(self):
        self.goal["report"] = "../outside.md"
        with self.assertRaises(Blocked):
            complete(self.root, self.state, "GOAL-001")


    def test_missing_criterion_evidence(self):
        self.goal["acceptance"][0]["evidence"] = ["migration/evidence/missing.txt"]
        with self.assertRaises(Blocked):
            complete(self.root, self.state, "GOAL-001")

    def test_criterion_evidence_escape(self):
        self.goal["acceptance"][0]["evidence"] = ["../outside.txt"]
        with self.assertRaises(Blocked):
            complete(self.root, self.state, "GOAL-001")

    def test_criterion_evidence_exists(self):
        p = self.root / "migration/evidence/proof.txt"
        p.parent.mkdir(parents=True)
        p.write_text("verified")
        self.goal["acceptance"][0]["evidence"] = ["migration/evidence/proof.txt"]
        self.assertTrue(complete(self.root, self.state, "GOAL-001"))
        inspect(self.root, self.state)

    def test_empty_criterion_evidence_array(self):
        self.goal["acceptance"][0]["evidence"] = []
        self.assertTrue(complete(self.root, self.state, "GOAL-001"))

    def test_all_evidence_entries_are_checked(self):
        proof = self.root / "migration/evidence/proof.txt"
        proof.parent.mkdir(parents=True)
        proof.write_text("verified")
        self.goal["evidence"] = ["migration/evidence/proof.txt"]
        self.goal["acceptance"][0]["evidence"] = [
            "migration/evidence/proof.txt", "migration/evidence/missing.txt"
        ]
        with self.assertRaises(Blocked):
            complete(self.root, self.state, "GOAL-001")
        self.assertEqual(self.goal["status"], "VALIDATING")

    def test_non_array_evidence_rejected(self):
        for container in (self.goal, self.goal["acceptance"][0]):
            for value in (self.goal["report"], None, {}, True):
                with self.subTest(container=container, value=value):
                    container["evidence"] = value
                    with self.assertRaises(Blocked):
                        complete(self.root, self.state, "GOAL-001")
                    self.assertEqual(self.goal["status"], "VALIDATING")
            container["evidence"] = []

    def test_criterion_evidence_symlink_escape(self):
        with tempfile.TemporaryDirectory() as outside:
            proof = Path(outside) / "proof.txt"
            proof.write_text("outside")
            link = self.root / "migration/evidence"
            link.symlink_to(Path(outside), target_is_directory=True)
            self.goal["acceptance"][0]["evidence"] = ["migration/evidence/proof.txt"]
            with self.assertRaises(Blocked):
                complete(self.root, self.state, "GOAL-001")

    def test_string_false_not_authorized(self):
        self.goal["authorization"]["reportWrite"] = "false"
        with self.assertRaises(Blocked):
            complete(self.root, self.state, "GOAL-001")

    def test_completed_goal_without_authorization_rejected_on_inspect(self):
        self.goal["status"] = "COMPLETED"
        self.goal["authorization"]["reportWrite"] = False
        with self.assertRaises(Blocked):
            inspect(self.root, self.state)

    def test_transitive_incomplete_dependency_rejected(self):
        first = {"id": "GOAL-001", "status": "PENDING", "dependencies": []}
        second = dict(self.goal, id="GOAL-002", status="COMPLETED", dependencies=["GOAL-001"])
        third = dict(self.goal, id="GOAL-003", status="VALIDATING", dependencies=["GOAL-002"])
        self.state["goals"] = [first, second, third]
        with self.assertRaises(Blocked):
            complete(self.root, self.state, "GOAL-003")


if __name__ == "__main__":
    unittest.main()
