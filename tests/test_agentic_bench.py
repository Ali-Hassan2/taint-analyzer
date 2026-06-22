

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
