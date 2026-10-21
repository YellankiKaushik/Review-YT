"""Private startup configuration must fail safely and respect process overrides."""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location(
    "local_probe", Path(__file__).parents[1] / "scripts/local_probe.py"
)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)


@pytest.fixture
def private_config(tmp_path, monkeypatch):
    monkeypatch.setattr(probe, "ROOT", tmp_path)
    for key in (
        "YOUTUBE_API_KEY",
        "OPENROUTER_API_KEY",
        "BACKEND_API_TOKEN",
        "BACKEND_URL",
        "SUMMARY_ALLOW_PAID",
        "SUMMARY_FALLBACK_ENABLED",
    ):
        monkeypatch.delenv(key, raising=False)
    (tmp_path / "apps/web").mkdir(parents=True)
    (tmp_path / ".env").write_text(
        "YOUTUBE_API_KEY=unit-test-private-youtube\nBACKEND_API_TOKEN=unit-test-private-token\n"
    )
    (tmp_path / "apps/web/.env.local").write_text(
        "BACKEND_API_TOKEN=unit-test-private-token\nBACKEND_URL=http://127.0.0.1:5100\n"
    )
    return tmp_path


def test_cloud_key_is_optional_for_baseline_startup(private_config):
    report, _, good = probe.configuration()
    assert good and not report["openrouterPresent"]


def test_mismatched_private_files_reject_startup(private_config):
    path = private_config / "apps/web/.env.local"
    path.write_text(
        path.read_text().replace("unit-test-private-token", "different-unit-test-token")
    )
    assert not probe.configuration()[2]


def test_inherited_paid_setting_rejects_startup(private_config, monkeypatch):
    monkeypatch.setenv("SUMMARY_ALLOW_PAID", "true")
    report, _, good = probe.configuration()
    assert not good and not report["paidDisabled"]


def test_probe_output_never_contains_private_values(private_config, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["local_probe.py", "--configuration-only"])
    assert probe.main() == 0
    output = capsys.readouterr().out
    assert "unit-test-private" not in output
    assert json.loads(output)["tokensMatch"] is True
