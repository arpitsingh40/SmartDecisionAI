"""Free-tool providers — zero-network tests for the keyless builtins and free-first ordering.

Covers: Frankfurter handler (rate / rates / errors), handler registration,
genesis builtin capability mapping, builder connect showing builtins as included,
and free-tier-first tool suggestions.

Run: cd backend && python -m pytest tests/test_free_tools.py -q
"""
import os
import sys
import json

os.environ["MONGO_URL"] = ""
os.environ.setdefault("DISABLE_MCP", "1")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

import execution.handlers.frankfurter as fx
import genesis_router as gr
from genesis import map_capabilities
from execution.connections import suggest_tools_for_function
from db import genesis_pipelines_col, orgs_col, members_col, executives_col


class FakeResp:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload or {}
        self.text = text or json.dumps(self._payload)

    def json(self):
        return self._payload


@pytest.fixture
def fake_get(monkeypatch):
    calls = []

    def _get(url, params=None, timeout=None):
        calls.append({"url": url, "params": params or {}})
        return FakeResp(payload={"amount": 1.0, "base": "USD", "date": "2026-09-29",
                                 "rates": {"INR": 88.4, "EUR": 0.85}})

    monkeypatch.setattr(fx.httpx, "get", _get)
    return calls


def test_frankfurter_rate(fake_get):
    out = fx.handle("FRANKFURTER_RATE", {"base": "usd", "quote": "inr", "amount": 100})
    assert out["successful"] is True
    assert "1 USD = 88.4 INR" in out["result"]
    assert "100 USD = 8840.0 INR" in out["result"]
    assert fake_get[0]["params"] == {"from": "USD", "to": "INR"}


def test_frankfurter_rates(fake_get):
    out = fx.handle("FRANKFURTER_RATES", {"base": "USD", "quotes": "INR,EUR"})
    assert out["successful"] is True
    assert "1 USD = 88.4 INR" in out["result"] and "1 USD = 0.85 EUR" in out["result"]
    assert fake_get[0]["params"] == {"from": "USD", "to": "INR,EUR"}


def test_frankfurter_errors(fake_get):
    missing = fx.handle("FRANKFURTER_RATE", {"base": "USD"})
    assert missing["successful"] is False and "Missing" in missing["error"]
    unknown = fx.handle("FRANKFURTER_DOES_NOT_EXIST", {})
    assert unknown["successful"] is False and "Unsupported" in unknown["error"]


def test_handler_registered():
    from execution.handlers import get_handler
    assert get_handler("FRANKFURTER_RATE") is fx.handle


def test_frankfurter_is_builtin_for_invoicing():
    caps = map_capabilities({"industry": "solar"})
    invoicing = next(c for c in caps if c["capability"] == "invoicing")
    assert "frankfurter" in invoicing.get("builtin", [])


def test_free_tier_first_suggestions():
    rows = suggest_tools_for_function("finance")
    assert rows[0]["toolkit"] == "frankfurter" and rows[0]["builtin"] is True
    assert rows[1]["toolkit"] == "stripe" and rows[1]["free"] is True


def test_genesis_connect_marks_builtins(monkeypatch):
    for col in (genesis_pipelines_col, orgs_col, members_col, executives_col):
        col.delete_many({})
    monkeypatch.setattr(gr, "extract_twin", lambda vision: {
        "twin": {"industry": "solar", "stage": "pre-revenue", "current_arr": 0,
                 "currency": "₹", "team_size": 1, "runway_months": 12,
                 "constraints": [], "fears": [], "strategic_forks": [],
                 "founder_bottleneck": "", "what_they_have": []},
        "questions": [],
    })
    user = {"id": "free-tools-user"}
    gr.genesis_start(gr.StartIn(vision="Build a rooftop solar company in India."), user=user)
    out = gr.genesis_connect(user=user)
    builtins = [c for c in out["connections"] if c["status"] == "builtin"]
    assert any(c["toolkit"] == "frankfurter" for c in builtins)
    assert all(c["toolkit"] != "none" for c in out["connections"])
