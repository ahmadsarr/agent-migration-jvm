#!/usr/bin/env python3
"""Run Spec Kit commands through OpenCode, recording invocations for review."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import uuid


TOOLKIT_VERSION = (Path(__file__).resolve().parents[1] / "VERSION").read_text(encoding="utf-8").strip()
SPEC_KIT_VERSION = "1.2.2"
STAGES = ("constitution", "specify", "plan", "tasks", "analyze", "implement", "converge")
CONTEXT = """Use the project's existing instructions and jvm-spark-migration skill if available.
Scope this invocation to the requested Spec Kit stage and feature directory.
Preserve explicit application behavior during JVM/library migration. Inspect existing
assertions and reuse adequate tests; add only missing tests for concrete critical
dependency or JDK-sensitive risks. Plan equivalent baseline and target runs and
record exact versions, actual executed checks and evidence. Missing runs are NOT_RUN.
Do not invent compatibility, business contracts, approvals or test results. Report
unresolved questions for human review rather than silently deciding them. Follow
the project's authorization scope for edits and tests. Do not merge or deploy.
"""


class WorkflowError(Exception):
    pass


def contained(root, relative):
    path = root / relative
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise WorkflowError("Path escapes project: " + str(relative))
    return resolved


def nonempty(path):
    if not path.is_file() or not path.stat().st_size:
        raise WorkflowError("Required file missing or empty: " + str(path))
    return path


def read_input(path):
    text = path.read_text(encoding="utf-8")
    if not text.strip():
        raise WorkflowError("Input file is empty: " + str(path))
    return text


def feature_path(value):
    path = Path(value)
    if path.is_absolute() or len(path.parts) < 2 or path.parts[0] != "specs" or ".." in path.parts:
        raise WorkflowError("--feature must be a project-relative path under specs/")
    return path.as_posix()


def artifact_names(stage, feature):
    if stage == "constitution":
        return [".specify/memory/constitution.md"]
    names = {
        "specify": ["spec.md"], "plan": ["spec.md", "plan.md"],
        "tasks": ["spec.md", "plan.md", "tasks.md"],
        "analyze": ["spec.md", "plan.md", "tasks.md"],
        "implement": ["spec.md", "plan.md", "tasks.md"],
        "converge": ["spec.md", "plan.md", "tasks.md"],
    }
    return [feature + "/" + name for name in names[stage]]


def prerequisites(root, stage, feature):
    nonempty(contained(root, ".opencode/commands/speckit." + stage + ".md"))
    if stage != "constitution":
        constitution = nonempty(contained(root, ".specify/memory/constitution.md"))
        if "[PROJECT_NAME]" in constitution.read_text(encoding="utf-8"):
            raise WorkflowError("Constitution is still a template; run constitution first")
    before = {"plan": "specify", "tasks": "plan", "analyze": "tasks",
              "implement": "tasks", "converge": "tasks"}.get(stage)
    if before:
        for name in artifact_names(before, feature):
            nonempty(contained(root, name))
        spec = contained(root, feature + "/spec.md").read_text(encoding="utf-8")
        if "[NEEDS CLARIFICATION" in spec:
            raise WorkflowError("Resolve the specification's NEEDS CLARIFICATION markers before continuing")


def fingerprints(root, names):
    result = {}
    for name in names:
        path = contained(root, name)
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return result


def git_head(root):
    if not shutil.which("git"):
        return None
    p = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root,
                       capture_output=True, text=True, timeout=10)
    return p.stdout.strip() if p.returncode == 0 else None


def call_process(argv, root, env, output, errors, timeout):
    with output.open("w", encoding="utf-8") as out, errors.open("w", encoding="utf-8") as err:
        process = subprocess.Popen(argv, cwd=root, env=env, stdin=subprocess.DEVNULL,
                                   stdout=out, stderr=err, start_new_session=os.name == "posix")
        try:
            return process.wait(timeout=timeout)
        except (subprocess.TimeoutExpired, KeyboardInterrupt):
            if os.name == "posix":
                os.killpg(process.pid, signal.SIGKILL)
            else:
                process.kill()
            process.wait()
            raise


def check_events(path):
    seen = False
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as error:
                raise WorkflowError("OpenCode did not return JSON events; inspect stdout.jsonl") from error
            if not isinstance(event, dict):
                raise WorkflowError("Unexpected OpenCode event format")
            if event.get("type") == "error":
                raise WorkflowError("OpenCode reported an error event; inspect stdout.jsonl")
            if event.get("type") in ("text", "step_finish"):
                seen = True
    if not seen:
        raise WorkflowError("No OpenCode text or completion event was recorded")


def opencode_command(stage, prompt, model):
    argv = ["opencode", "run", "--command", "speckit." + stage, "--format", "json"]
    if model:
        argv += ["--model", model]
    # Keep the entire prompt one positional argument, even if it starts with '-'.
    return argv + ["--", prompt]


def init_preflight(root):
    for name in (".specify", ".opencode/commands", ".opencode/command"):
        contained(root, name)
    if os.path.lexists(root / ".specify"):
        raise WorkflowError("Spec Kit already exists; init will not overwrite .specify")
    for folder in ("commands", "command"):
        if list((root / ".opencode" / folder).glob("speckit.*")):
            raise WorkflowError("Existing Spec Kit commands found; review them before initialization")


def execute(args):
    root = args.project.resolve()
    if not root.is_dir():
        raise WorkflowError("Project directory does not exist")
    if args.timeout <= 0:
        raise WorkflowError("--timeout must be positive")
    feature = None
    if args.action == "init":
        init_preflight(root)
        jobs = [("init", ["specify", "init", "--here", "--integration", "opencode",
                          "--script", "py", "--non-interactive", "--ignore-agent-tools", "--force"])]
    else:
        if args.action == "prepare" or args.stage != "constitution":
            if not args.feature:
                raise WorkflowError("--feature is required for feature stages")
            feature = feature_path(args.feature)
            contained(root, feature)
        if args.action == "prepare":
            spec = read_input(args.spec_file)
            plan = read_input(args.plan_file)
            for name in ("spec.md", "plan.md", "tasks.md"):
                if os.path.lexists(root / feature / name):
                    raise WorkflowError("prepare requires a new feature; use run for explicit retries")
            steps = [("specify", spec), ("plan", plan), ("tasks", "Generate tasks for this feature."),
                     ("analyze", "Review consistency and report unresolved findings.")]
        else:
            if args.stage in ("constitution", "specify", "plan") and not args.input_file:
                raise WorkflowError("--input-file is required for this stage")
            steps = [(args.stage, read_input(args.input_file) if args.input_file else "Run the requested stage.")]
        jobs = []
        for stage, text in steps:
            prompt = CONTEXT + "\nRequested stage: " + stage + "\n"
            if feature:
                prompt += "SPECIFY_FEATURE_DIRECTORY=" + feature + "\n"
            prompt += "\nUser input:\n" + text
            jobs.append((stage, opencode_command(stage, prompt, args.model)))
        # Check every command before launching a multi-stage preparation.
        for stage, _ in jobs:
            nonempty(contained(root, ".opencode/commands/speckit." + stage + ".md"))
        prerequisites(root, jobs[0][0], feature)

    if args.dry_run:
        print(json.dumps({"project": str(root), "feature": feature, "commands": [a for _, a in jobs]}, indent=2))
        return 0
    executable = jobs[0][1][0]
    if not shutil.which(executable):
        raise WorkflowError(executable + " is not installed or not on PATH")
    version = None
    if args.action == "init":
        p = subprocess.run(["specify", "version", "--json"], cwd=root, capture_output=True,
                           text=True, timeout=30, stdin=subprocess.DEVNULL)
        if p.returncode:
            raise WorkflowError("Cannot read Spec Kit version; install specify-cli==" + SPEC_KIT_VERSION)
        version = json.loads(p.stdout).get("cli_version")
        if version != SPEC_KIT_VERSION:
            raise WorkflowError("Supported Spec Kit version: " + SPEC_KIT_VERSION + "; found " + str(version))

    runs = contained(root, ".jvm-migration/speckit-runs")
    runs.mkdir(parents=True, exist_ok=True)
    run_dir = runs / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ-") + uuid.uuid4().hex[:12])
    run_dir.mkdir()
    report = {"toolkit_version": TOOLKIT_VERSION, "project": str(root), "feature": feature, "spec_kit_version": version,
              "status": "RUNNING", "review_required": True, "git_head_before": git_head(root), "steps": []}
    report_path = run_dir / "report.json"

    def persist():
        tmp = run_dir / "report.tmp"
        tmp.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        tmp.replace(report_path)

    env = os.environ.copy()
    # Feature selection is explicit; it must not follow an unrelated previous session.
    env.pop("SPECIFY_FEATURE_DIRECTORY", None)
    env.pop("SPECIFY_FEATURE", None)
    if feature:
        env["SPECIFY_FEATURE_DIRECTORY"] = feature
    print("Run report: " + str(report_path), flush=True)
    persist()
    try:
        for index, (stage, argv) in enumerate(jobs, 1):
            if stage != "init":
                prerequisites(root, stage, feature)
            step_dir = run_dir / (str(index) + "-" + stage)
            step_dir.mkdir()
            names = artifact_names(stage, feature) if stage != "init" else [
                ".opencode/commands/speckit." + name + ".md" for name in STAGES]
            step = {"stage": stage, "argv": argv, "status": "RUNNING",
                    "artifacts_before": fingerprints(root, names)}
            report["steps"].append(step)
            persist()
            print("Running " + stage + "...", flush=True)
            output = step_dir / ("stdout.log" if stage == "init" else "stdout.jsonl")
            code = call_process(argv, root, env, output, step_dir / "stderr.log", args.timeout)
            step["exit_code"] = code
            if code:
                raise WorkflowError(stage + " exited with code " + str(code))
            if stage != "init":
                check_events(output)
            for name in names:
                nonempty(contained(root, name))
            step["artifacts_after"] = fingerprints(root, names)
            step["status"] = "RETURNED_REVIEW_REQUIRED"
            persist()
        report["status"] = "RETURNED_REVIEW_REQUIRED"
        print("Commands returned; review artifacts, questions and test evidence before proceeding.")
        return 0
    except (WorkflowError, OSError, ValueError, subprocess.TimeoutExpired, KeyboardInterrupt) as error:
        report["status"] = "FAILED"
        report["error"] = type(error).__name__ + ": " + str(error)
        if report["steps"] and report["steps"][-1]["status"] == "RUNNING":
            report["steps"][-1]["status"] = "FAILED"
        raise
    finally:
        report["git_head_after"] = git_head(root)
        persist()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=TOOLKIT_VERSION)
    parser.add_argument("--project", required=True, type=Path)
    parser.add_argument("--model", help="OpenCode provider/model identifier; otherwise use its configured model")
    parser.add_argument("--timeout", type=float, default=900, help="Maximum seconds per subprocess")
    parser.add_argument("--dry-run", action="store_true", help="Show argv without running tools or writing files")
    actions = parser.add_subparsers(dest="action", required=True)
    actions.add_parser("init", help="Initialize fresh Spec Kit 1.2.2 scaffolding for OpenCode")
    prepare = actions.add_parser("prepare", help="Run specify, plan, tasks and analyze, then stop for review")
    prepare.add_argument("--feature", required=True)
    prepare.add_argument("--spec-file", required=True, type=Path)
    prepare.add_argument("--plan-file", required=True, type=Path)
    run = actions.add_parser("run", help="Explicitly invoke one stage, including implement/converge")
    run.add_argument("stage", choices=STAGES)
    run.add_argument("--feature")
    run.add_argument("--input-file", type=Path)
    args = parser.parse_args()
    try:
        return execute(args)
    except (WorkflowError, OSError, ValueError, subprocess.TimeoutExpired) as error:
        print("BLOCKED: " + str(error), file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrupted; inspect the run report before retrying.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
