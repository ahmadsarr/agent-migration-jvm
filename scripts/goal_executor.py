#!/usr/bin/env python3
"""Conservative, stdlib-only goal checkpoint verifier. Does not execute migration actions."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile


class Blocked(Exception):
    pass


def git(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if p.returncode:
        raise Blocked("Git inspection failed: " + p.stderr.strip())
    return p.stdout.strip()


def inside(root, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise Blocked("Expected nonempty relative path")
    resolved = (root / relative).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise Blocked("Path escapes project directory")
    return resolved


def inspect(root, state):
    if state.get("schemaVersion") != 1:
        raise Blocked("Unsupported state version")
    saved = state.get("repository", {})
    head = git(root, "rev-parse", "HEAD")
    branch = git(root, "branch", "--show-current")
    if saved.get("head") != head or saved.get("branch") != branch:
        raise Blocked("Git HEAD/branch divergence; reconcile manually")
    goals = state.get("goals")
    if not isinstance(goals, list):
        raise Blocked("Invalid goals collection")
    by_id = {g["id"]: g for g in goals}
    if len(by_id) != len(goals):
        raise Blocked("Duplicate goal ID")
    for g in goals:
        for dep in g.get("dependencies", []):
            if dep not in by_id:
                raise Blocked("Missing dependency: " + dep)
        if g.get("status") == "COMPLETED":
            verify_completed(root, g)
            verify_dependencies_and_authorization(g, by_id)
    return by_id


def verify_completed(root, goal):
    checks = goal.get("acceptance", [])
    if not checks or any(c.get("result") != "PASS" for c in checks):
        raise Blocked(goal["id"] + ": acceptance criteria not all PASS")
    report = inside(root, goal.get("report"))
    if not report.is_file() or not report.stat().st_size:
        raise Blocked(goal["id"] + ": persisted report missing or empty")
    evidence_paths = list(goal.get("evidence", []))
    for check in checks:
        if check.get("evidence") is not None:
            evidence_paths.append(check["evidence"])
    for item in evidence_paths:
        evidence = inside(root, item)
        if not evidence.is_file():
            raise Blocked(goal["id"] + ": evidence missing: " + item)


def verify_dependencies_and_authorization(goal, goals):
    if any(goals[dep]["status"] != "COMPLETED" for dep in goal["dependencies"]):
        raise Blocked(goal["id"] + ": dependencies not complete")
    if goal.get("authorization", {}).get("reportWrite") is not True:
        raise Blocked(goal["id"] + ": report persistence not authorized")


def complete(root, state, goal_id):
    goals = inspect(root, state)
    if goal_id not in goals:
        raise Blocked("Unknown goal")
    goal = goals[goal_id]
    if goal["status"] == "COMPLETED":
        return False
    if goal["status"] not in ("VALIDATING", "READY"):
        raise Blocked("Goal must be VALIDATING or READY")
    verify_dependencies_and_authorization(goal, goals)
    verify_completed(root, goal)
    goal["status"] = "COMPLETED"
    return True


def atomic_write(path, data):
    fd, tmp = tempfile.mkstemp(prefix=".state-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(data, out, indent=2)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--state", default="migration/state.json")
    parser.add_argument("command", choices=("status", "complete"))
    parser.add_argument("--goal")
    args = parser.parse_args()
    root = args.project.resolve()
    path = inside(root, args.state)
    if not path.is_file():
        raise Blocked("State file missing")
    state = json.loads(path.read_text(encoding="utf-8"))
    if args.command == "status":
        inspect(root, state)
        for goal in state["goals"]:
            print(goal["id"], goal["status"])
    else:
        if not args.goal:
            parser.error("--goal is required for complete")
        if complete(root, state, args.goal):
            atomic_write(path, state)
        print(args.goal, "COMPLETED")


if __name__ == "__main__":
    try:
        main()
    except (Blocked, KeyError, ValueError, OSError) as error:
        print("BLOCKED:", error, file=sys.stderr)
        sys.exit(2)
