from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "sync_tracking.py"
SPEC = importlib.util.spec_from_file_location("sync_tracking", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
tracking = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tracking)


def test_tracking_inventory_preserves_fields_and_excludes_navigation():
    streams = tracking.workstreams()
    assert len(streams) == 19
    assert len({stream["key"] for stream in streams}) == 19
    assert all(stream["marker"] in stream["body"] for stream in streams)
    assert all("GitHub issue:" not in stream["body"] for stream in streams)
    assert all("99_" not in stream["path"].name for stream in streams)


def test_preview_never_writes_or_mutates_and_detects_remote_edits(monkeypatch, capsys):
    streams = tracking.workstreams()
    stream = streams[0]
    repo_issue = {
        "body": stream["body"],
        "title": stream["title"],
        "state": "closed",
        "state_reason": "completed",
        "html_url": "https://github.com/Zanark/StonksSniper/issues/1",
        "number": 1,
    }

    def fake_gh(*args, **kwargs):
        assert kwargs.get("payload") is None
        if args == ("api", "user"):
            return {"login": "Zanark"}
        if args == ("api", "repos/Zanark/StonksSniper"):
            return {"visibility": "public"}
        if args[1].startswith("repos/Zanark/StonksSniper/issues?"):
            return [[repo_issue]]
        raise AssertionError(f"Unexpected operation: {args}")

    monkeypatch.setattr(tracking, "gh", fake_gh)
    monkeypatch.setattr(
        tracking,
        "graphql",
        lambda *_args, **_kwargs: {
            "node": {
                "title": "StonksSniper",
                "fields": {
                    "nodes": [
                        {
                            "id": "status",
                            "name": "Status",
                            "options": [
                                {"id": name, "name": name}
                                for name in ("Todo", "In Progress", "Done")
                            ],
                        }
                    ]
                },
            }
        },
    )
    monkeypatch.setattr(
        tracking,
        "project_items",
        lambda _: {repo_issue["html_url"]: {"id": "item", "status": "Done"}},
    )
    monkeypatch.setattr(tracking, "save", lambda _: pytest.fail("Preview attempted a save"))
    # Test independent of real adoption baselines created later.
    config = tracking.json.loads(tracking.CONFIG.read_text(encoding="utf-8"))
    config["workstreams"] = {}
    monkeypatch.setattr(
        tracking,
        "CONFIG",
        type("Config", (), {"read_text": staticmethod(lambda **_: tracking.json.dumps(config))})(),
    )
    tracking.sync(False, stream["key"])
    assert "Preview only" in capsys.readouterr().out
    repo_issue["body"] += "\nHuman-authored change"
    with pytest.raises(ValueError, match="differs"):
        tracking.sync(False, stream["key"])


@pytest.mark.parametrize("converges", [True, False])
def test_mapping_verification_retries_reads_only_and_has_a_bound(monkeypatch, converges):
    issue = {
        "number": 2,
        "html_url": "https://github.com/Zanark/StonksSniper/issues/2",
        "body": "Managed body",
        "title": "Managed title",
        "state": "open",
    }
    reads = []
    sleeps = []
    statuses = iter([None, "Todo", "In Progress" if converges else "Todo", "Todo"])

    def read_issue(*args, **kwargs):
        assert not kwargs
        reads.append(args)
        return issue

    def read_project(_):
        status = next(statuses)
        return {} if status is None else {issue["html_url"]: {"id": "item", "status": status}}

    monkeypatch.setattr(tracking, "gh", read_issue)
    monkeypatch.setattr(tracking, "project_items", read_project)
    monkeypatch.setattr(tracking.time, "sleep", sleeps.append)
    stream = {"key": "SS-02", "title": issue["title"], "body": issue["body"]}
    if converges:
        verified_issue, item = tracking.verify_mapping(
            "Zanark/StonksSniper", "project", stream, issue, "open", "In Progress"
        )
        assert verified_issue == issue
        assert item["status"] == "In Progress"
        assert sleeps == [0.5, 1]
    else:
        with pytest.raises(RuntimeError, match="bounded reads"):
            tracking.verify_mapping(
                "Zanark/StonksSniper", "project", stream, issue, "open", "In Progress"
            )
        assert sleeps == [0.5, 1, 2]
    assert reads == [("api", "repos/Zanark/StonksSniper/issues/2")] * (3 if converges else 4)
