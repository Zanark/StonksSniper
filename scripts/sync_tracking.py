"""Explicit, local-source-of-truth TODO/issue/Project sync; no scheduler or credentials stored."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "TODO" / "tracking.json"


def gh(*arguments: str, payload: dict[str, Any] | None = None) -> Any:
    command = ["gh", *arguments]
    if payload is not None:
        command.extend(["--input", "-"])
    process = subprocess.run(
        command,
        input=json.dumps(payload) if payload is not None else None,
        text=True,
        capture_output=True,
        check=False,
    )
    if process.returncode:
        raise RuntimeError(process.stderr.strip() or "GitHub command failed.")
    return json.loads(process.stdout) if process.stdout.strip() else None


def graphql(query: str, **variables: Any) -> Any:
    response = gh("api", "graphql", payload={"query": query, "variables": variables})
    if response.get("errors"):
        raise RuntimeError(json.dumps(response["errors"]))
    return response["data"]


def save(config: dict[str, Any]) -> None:
    temporary = CONFIG.with_suffix(".tmp")
    temporary.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    temporary.replace(CONFIG)


def digest(body: str) -> str:
    return hashlib.sha256(body.encode()).hexdigest()


def workstreams() -> list[dict[str, Any]]:
    result = []
    required = (
        "Purpose",
        "Tasks",
        "Acceptance criteria",
        "Completion evidence",
        "Completion log",
    )
    for path in sorted((ROOT / "TODO").glob("*.todo")):
        if path.name.startswith(("00_", "99_")):
            continue
        text = path.read_text(encoding="utf-8")
        for field in ("Workstream ID", "Status", "Milestone", "Dependencies", "GitHub issue"):
            if not re.search(rf"^{field}: .+$", text, re.MULTILINE):
                raise ValueError(f"{path.name}: missing {field}.")
        for section in required:
            if f"\n## {section}\n" not in text:
                raise ValueError(f"{path.name}: missing {section}.")
        key_match = re.search(r"^Workstream ID: (SS-\d+)$", text, re.MULTILINE)
        status_match = re.search(r"^Status: (\w+)$", text, re.MULTILINE)
        if key_match is None or status_match is None:
            raise ValueError(f"{path.name}: invalid stable identity or status.")
        key, status = key_match[1], status_match[1]
        marker = f"<!-- stonkssniper-workstream:{key} -->"
        body = re.sub(r"^GitHub issue: .*\n", "", text, flags=re.MULTILINE)
        result.append(
            {
                "key": key,
                "status": status,
                "path": path,
                "marker": marker,
                "title": text.splitlines()[0].removeprefix("# "),
                "body": marker + "\n\n" + body,
            }
        )
    if len({item["key"] for item in result}) != len(result):
        raise ValueError("Duplicate workstream identity.")
    return result


def project_items(project_id: str) -> dict[str, dict[str, str | None]]:
    result = {}
    cursor = None
    while True:
        data = graphql(
            """query($id:ID!,$cursor:String) { node(id:$id) { ... on ProjectV2 {
              items(first:100,after:$cursor) { pageInfo { hasNextPage endCursor }
                nodes { id content { ... on Issue { id url } }
                  fieldValues(first:30) { nodes { ... on ProjectV2ItemFieldSingleSelectValue {
                    name field { ... on ProjectV2SingleSelectField { name } }
                  } } } }
              } } } }""",
            id=project_id,
            cursor=cursor,
        )["node"]["items"]
        for item in data["nodes"]:
            content = item["content"]
            if not content or "url" not in content:
                continue
            status = next(
                (
                    value["name"]
                    for value in item["fieldValues"]["nodes"]
                    if value.get("field", {}).get("name") == "Status"
                ),
                None,
            )
            if content["url"] in result:
                raise ValueError(f"Duplicate Project issue item: {content['url']}")
            result[content["url"]] = {"id": item["id"], "status": status}
        if not data["pageInfo"]["hasNextPage"]:
            return result
        cursor = data["pageInfo"]["endCursor"]


def verify_mapping(
    repo: str,
    project_id: str,
    stream: dict[str, Any],
    issue: dict[str, Any],
    desired_state: str,
    project_status: str,
) -> tuple[dict[str, Any], dict[str, str | None]]:
    # Project field mutations may be acknowledged before read queries reflect them.
    for delay in (0, 0.5, 1, 2):
        if delay:
            time.sleep(delay)
        verified_issue = gh("api", f"repos/{repo}/issues/{issue['number']}")
        verified_item = project_items(project_id).get(issue["html_url"])
        if (
            verified_issue["body"] == stream["body"]
            and verified_issue["title"] == stream["title"]
            and verified_issue["state"] == desired_state
            and (desired_state != "closed" or verified_issue["state_reason"] == "completed")
            and verified_item is not None
            and verified_item["status"] == project_status
        ):
            return verified_issue, verified_item
    raise RuntimeError(f"{stream['key']}: read-back verification failed after bounded reads.")


def sync(apply: bool, only: str | None) -> None:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    if gh("api", "user")["login"].lower() != "zanark":
        raise ValueError("Authenticated identity must be Zanark.")
    repo = config["repository"]
    repository = gh("api", f"repos/{repo}")
    if repo != "Zanark/StonksSniper" or repository["visibility"] != "public":
        raise ValueError("Unexpected repository or visibility; reconcile adoption first.")
    project_id = config["project"]["id"]
    project = graphql(
        """query($id:ID!) { node(id:$id) { ... on ProjectV2 { title
          fields(first:100) { nodes { ... on ProjectV2SingleSelectField {
            id name options { id name } } } } } } }""",
        id=project_id,
    )["node"]
    if project["title"] != "StonksSniper":
        raise ValueError("Unexpected target Project.")
    status_field = next(
        field for field in project["fields"]["nodes"] if field.get("name") == "Status"
    )
    options = {option["name"]: option["id"] for option in status_field["options"]}
    if not set(config["status_mapping"].values()).issubset(options):
        raise ValueError("Configured Project statuses are absent; no field changes were made.")
    pages = gh("api", f"repos/{repo}/issues?state=all&per_page=100", "--paginate", "--slurp")
    issues = [issue for page in pages for issue in page if "pull_request" not in issue]
    items = project_items(project_id)
    streams = workstreams()
    if only is not None:
        streams = [stream for stream in streams if stream["key"] == only]
        if not streams:
            raise ValueError(f"No workstream {only}.")
    plan = []
    for stream in streams:
        key = stream["key"]
        if stream["status"] not in config["status_mapping"]:
            raise ValueError(f"{key}: unsupported status.")
        matches = [issue for issue in issues if stream["marker"] in (issue["body"] or "")]
        if len(matches) > 1:
            raise ValueError(f"{key}: duplicate recovery markers.")
        issue = matches[0] if matches else None
        record = config["workstreams"].get(key, {})
        if record.get("issue_url") and (issue is None or issue["html_url"] != record["issue_url"]):
            raise ValueError(f"{key}: mapped issue missing or identity changed.")
        project_status = config["status_mapping"][stream["status"]]
        desired_state = "closed" if stream["status"] == "DONE" else "open"
        item = items.get(issue["html_url"]) if issue else None
        if issue:
            baseline = record.get("baseline")
            observed = {
                "body_sha256": digest(issue["body"] or ""),
                "title": issue["title"],
                "issue_state": issue["state"],
                "state_reason": issue["state_reason"],
                "project_status": item["status"] if item else None,
            }
            if baseline and observed != baseline:
                raise ValueError(f"{key}: remote change since last sync; reconcile before writing.")
            if not baseline and (
                issue["body"] != stream["body"]
                or issue["title"] != stream["title"]
                or issue["state"] != desired_state
            ):
                raise ValueError(f"{key}: unbaselined remote issue differs; manual reconciliation.")
        action = "create issue + item" if not issue else "verify/update owned mapping"
        print(f"{key}: {action}; {desired_state}; Project={project_status}; {stream['path'].name}")
        plan.append((stream, issue, item, project_status, desired_state))
    print("Excluded: 00_INDEX.todo and 99_DEVELOPMENT_LEDGER.todo. No draft items or scheduling.")
    if not apply:
        print("Preview only; no remote or local writes.")
        return
    for stream, issue, item, project_status, desired_state in plan:
        key = stream["key"]
        if issue is None:
            issue = gh(
                "api",
                f"repos/{repo}/issues",
                payload={
                    "title": stream["title"],
                    "body": stream["body"],
                },
            )
        record = config["workstreams"].setdefault(key, {})
        record.update({"issue_url": issue["html_url"], "issue_number": issue["number"]})
        save(config)
        if issue["body"] != stream["body"] or issue["title"] != stream["title"]:
            issue = gh(
                "api",
                f"repos/{repo}/issues/{issue['number']}",
                "--method",
                "PATCH",
                payload={"body": stream["body"], "title": stream["title"]},
            )
        if issue["state"] != desired_state:
            issue = gh(
                "api",
                f"repos/{repo}/issues/{issue['number']}",
                "--method",
                "PATCH",
                payload={
                    "state": desired_state,
                    "state_reason": "completed" if desired_state == "closed" else "reopened",
                },
            )
        if item is None:
            item_id = graphql(
                """mutation($project:ID!,$content:ID!) {
                  addProjectV2ItemById(input:{projectId:$project,contentId:$content}) {
                    item { id } } }""",
                project=project_id,
                content=issue["node_id"],
            )["addProjectV2ItemById"]["item"]["id"]
        else:
            item_id = item["id"]
        if item is None or item["status"] != project_status:
            graphql(
                """mutation($project:ID!,$item:ID!,$field:ID!,$option:String!) {
                  updateProjectV2ItemFieldValue(input:{projectId:$project,itemId:$item,
                    fieldId:$field,value:{singleSelectOptionId:$option}}) {
                    projectV2Item { id } } }""",
                project=project_id,
                item=item_id,
                field=status_field["id"],
                option=options[project_status],
            )
        verified_issue, verified_item = verify_mapping(
            repo, project_id, stream, issue, desired_state, project_status
        )
        record["item_id"] = item_id
        record["baseline"] = {
            "body_sha256": digest(verified_issue["body"]),
            "title": verified_issue["title"],
            "issue_state": verified_issue["state"],
            "state_reason": verified_issue["state_reason"],
            "project_status": verified_item["status"],
        }
        source = stream["path"].read_text(encoding="utf-8")
        source = re.sub(
            r"^GitHub issue: .+$", f"GitHub issue: {issue['html_url']}", source, flags=re.MULTILINE
        )
        stream["path"].write_text(source, encoding="utf-8")
        save(config)
        print(f"Verified {key}: {issue['html_url']}; item={item_id}; {project_status}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="Apply the previewed adoption.")
    parser.add_argument("--only", help="Pilot one stable workstream ID, for example SS-01.")
    arguments = parser.parse_args()
    try:
        sync(arguments.apply, arguments.only)
    except (ValueError, KeyError, RuntimeError, OSError, StopIteration) as error:
        raise SystemExit(f"Tracking sync stopped: {error}") from error
