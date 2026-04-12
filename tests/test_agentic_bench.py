"""
HTTP-style integration tests: in-process FastAPI client posts agent code like a real client.
Results are persisted under reports/ for inspection.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "agent_bench" / "manifest.json"
AGENTS_DIR = ROOT / "agent_bench" / "agents"
REPORT_PATH = ROOT / "reports" / "agentic_bench_last.json"


def _collect_rule_hits(issues: list[dict]) -> set[str]:
    hits: set[str] = set()
    for item in issues:
        r = item.get("rule")
        if r:
            hits.add(str(r))
    return hits


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_agentic_benchmark_scan_and_store_results(client: TestClient) -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    runs: list[dict] = []

    for agent in manifest["agents"]:
        path = AGENTS_DIR / agent["path"]
        code = path.read_text(encoding="utf-8")
        resp = client.post(
            "/api/v1/scan/scan_model",
            json={"filename": agent["path"], "code": code},
        )
        assert resp.status_code == 200, resp.text
        body = resp.json()
        issues = body.get("issues_details", [])
        rules_hit = _collect_rule_hits(issues)

        for required in agent.get("must_contain_rules", []):
            assert required in rules_hit, (
                f"Agent {agent['id']}: expected rule {required!r} in {sorted(rules_hit)} "
                f"(issues_count={body.get('issues_count')})"
            )

        runs.append(
            {
                "agent_id": agent["id"],
                "agent_file": agent["path"],
                "project_id": body.get("project_id"),
                "issues_count": body.get("issues_count"),
                "summary": body.get("summary"),
                "pipeline": body.get("pipeline"),
                "rules_hit": sorted(rules_hit),
            }
        )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        json.dumps({"manifest": manifest["description"], "runs": runs}, indent=2),
        encoding="utf-8",
    )
