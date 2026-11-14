"""Collect reproducible T02 operational evidence without reading ground truth.

    python -m tools.report_t02_results

Official quality metrics must still come from src.evaluate with instructor GT.
"""
from __future__ import annotations

import json
import hashlib
import importlib.metadata
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from src.common.context import RunContext
from src.common.io import resolve_config
from src.common.manifest import verify_manifest
from src.common.review import AuditLog
from src.pipeline import load, process


def main() -> int:
    report = Path("reports")
    evidence = report / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    cfg = resolve_config("configs/lab.yaml", "t02")
    input_dir = Path(cfg["input"])
    analysis_dir = Path("out/report_analysis")
    analysis_dir.mkdir(parents=True, exist_ok=True)
    ctx = RunContext(track="t02", input_dir=input_dir, output_dir=analysis_dir,
                     config=cfg, seed=42, rng=np.random.default_rng(42),
                     audit=AuditLog(analysis_dir / "audit_log.jsonl"))
    data = load(ctx)
    features = process(ctx, data)
    meta = data["images"]
    eval_meta = meta[meta.split == "eval"]
    runs = {}
    queues = {}
    decisions = {}
    evaluation = {}
    comparison = features[features.split == "eval"].copy()
    for name in ("baseline", "poc"):
        run_dir = Path("out") / name
        info = json.loads((run_dir / "run_info.json").read_text(encoding="utf-8"))
        if info["status"] != 0:
            raise ValueError(f"{name} run failed; run src.main first")
        runs[name] = info
        queue = pd.read_csv(run_dir / "review_queue.csv")
        queues[name] = queue
        decisions[name] = json.loads((run_dir / "decision.json").read_text(encoding="utf-8"))
        ranked = pd.read_csv(run_dir / "ranked_review.csv")
        assert ranked.image_id.is_unique and set(ranked.image_id) == set(meta.image_id)
        ranked = ranked[ranked.image_id.isin(eval_meta.image_id)].reset_index(drop=True)
        assert len(queue) == 20 and queue.image_id.tolist() == ranked.image_id.head(20).tolist()
        ranked[f"{name}_eval_rank"] = np.arange(1, len(ranked) + 1)
        comparison = comparison.merge(ranked[["image_id", f"{name}_eval_rank"]], on="image_id", validate="one_to_one")
        dest = evidence / name
        dest.mkdir(parents=True, exist_ok=True)
        for filename in ("run_info.json", "ranked_review.csv", "review_queue.csv", "decision.json",
                         "decision_log.csv", "audit_log.jsonl"):
            shutil.copy2(run_dir / filename, dest / filename)
        for filename in ("review_queue_reviewed.csv", "senior_review_queue_reviewed.csv", "domain_owner_review_queue_reviewed.csv"):
            if (run_dir / filename).exists():
                shutil.copy2(run_dir / filename, dest / filename)
        command = [sys.executable, "-m", "src.evaluate", "--track", "t02", "--pred",
                   str(run_dir / "ranked_review.csv"), "--run-name", name,
                   "--out", str(report / f"metrics_{name}.json")]
        result = subprocess.run(command, capture_output=True, text=True)
        evaluation[name] = {"command": command[1:], "exit_code": result.returncode,
                            "stdout": result.stdout, "stderr": result.stderr}
    comparison = comparison.sort_values("poc_eval_rank")
    comparison.to_csv(report / "ranking_diagnostics.csv", index=False)
    slice_rows = []
    for column in ("light", "camera_id"):
        for value, sub in eval_meta.groupby(column):
            row = {"slice": f"{column}={value}", "eval_n": len(sub)}
            for name, queue in queues.items():
                n = int(queue[column].eq(value).sum())
                row[f"{name}_selected"] = n
                row[f"{name}_selection_rate"] = n / len(sub)
            slice_rows.append(row)
    pd.DataFrame(slice_rows).to_csv(report / "queue_slices.csv", index=False)
    tests_path = Path("out/pytest_report.txt")
    test_result = {}
    if tests_path.exists():
        raw = tests_path.read_bytes()
        log = raw.decode("utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig")
        (evidence / "pytest_report.txt").write_text(log, encoding="utf-8")
        test_result = {"passed": len(re.findall(r"^PASSED ", log, re.M)),
                       "skipped": sum(int(n) for n in re.findall(r"^SKIPPED \[(\d+)\]", log, re.M)),
                       "failed": len(re.findall(r"^FAILED ", log, re.M)),
                       "errors": len(re.findall(r"^ERROR ", log, re.M))}
    preflight = Path("out/preflight_report.txt")
    if preflight.exists():
        raw = preflight.read_bytes()
        (evidence / "preflight_report.txt").write_text(
            raw.decode("utf-16" if raw.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"), encoding="utf-8")
    (evidence / "git_contributions.txt").write_text(
        subprocess.check_output(["git", "log", "HEAD", "--format=%h | %an <%ae> | %s", "-16"], text=True, encoding="utf-8"), encoding="utf-8")
    manifests = {p.parent.name: verify_manifest(p) for p in sorted(Path("fixtures").glob("*/manifest.csv"))}
    overlap = len(set(queues["baseline"].image_id) & set(queues["poc"].image_id))
    summary = {
        "track": "t02", "seed": 42, "budget": 20, "data_n": len(meta),
        "split_counts": {str(k): int(v) for k, v in meta.split.value_counts().items()},
        "scene_counts": {str(k): int(v) for k, v in meta.assign(scene=meta.image_id.str.rsplit("_", n=1).str[0]).groupby("split").scene.nunique().items()},
        "manifest_count": len(manifests), "manifest_problems": manifests,
        "quality_metrics_status": "available" if all(v["exit_code"] == 0 for v in evaluation.values()) else "unavailable; see evaluation_attempts",
        "evaluation_attempts": evaluation, "runs": runs, "decisions": decisions,
        "top20_overlap": overlap, "top20_jaccard": overlap / (40 - overlap),
        "tests": test_result,
        "package_versions": {name: importlib.metadata.version(name) for name in
                             ("numpy", "pandas", "Pillow", "scipy", "PyYAML", "pytest")},
        "warning": "Selection rates and overlap are operational diagnostics, not recall, precision or false-alarm rates.",
    }
    (report / "results_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = ["# So sánh vận hành baseline và PoC", "", "Sinh bằng `python -m tools.report_t02_results`. Chưa có GT để so sánh chất lượng.", "",
            "| Chỉ tiêu | Baseline | PoC |", "|---|---:|---:|"]
    for label, values in (
        ("Ảnh được xếp hạng", [r["stats"]["ranked_n"] for r in runs.values()]),
        ("Ảnh trong queue eval", [len(q) for q in queues.values()]),
        ("Exit code", [r["status"] for r in runs.values()]),
        ("Runtime toàn pipeline (s)", [r["runtime_seconds"] for r in runs.values()]),
        ("Runtime / 100 ảnh (s)", [round(r["runtime_seconds"] * 100 / len(meta), 4) for r in runs.values()]),
        ("Xử lý feature + score (ms/ảnh)", [r["stats"]["process_ms_per_image"] for r in runs.values()]),
        ("Quyết định queue", [d["status"] for d in decisions.values()]),
    ):
        rows.append(f"| {label} | {values[0]} | {values[1]} |")
    rows.extend(["| Defect Recall@20 | Chưa có GT | Chưa có GT |",
                 "| Precision@20 | Chưa có GT | Chưa có GT |", "",
                 f"Top-20 giao nhau: {overlap}/20; Jaccard: {overlap / (40 - overlap):.4f}.",
                 "Runtime là một lượt chạy cục bộ, chưa phải benchmark; thời gian review của người dùng chưa được đo."])
    (report / "operational_comparison.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    paths = sorted(p for p in evidence.rglob("*") if p.is_file())
    paths += [report / name for name in ("results_summary.json", "ranking_diagnostics.csv", "queue_slices.csv", "operational_comparison.md")]
    pd.DataFrame([{"path": p.relative_to(report).as_posix(), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                  for p in paths]).to_csv(report / "evidence_manifest.csv", index=False)
    print(json.dumps({"tests": test_result, "overlap": overlap, "slices": slice_rows,
                      "evaluation_exit_codes": {k: v["exit_code"] for k, v in evaluation.items()}}, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
