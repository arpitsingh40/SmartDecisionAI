"""Genesis builder pipeline — end-to-end smoke with zero LLM calls (mongomock in-process).

Covers the wizard the landing story depends on:
vision -> twin/questions -> mission -> organization+executives -> launch tasks.

Run: cd backend && python -m pytest tests/test_genesis_flow.py -q
"""
import os
import sys

os.environ["MONGO_URL"] = ""
os.environ.setdefault("DISABLE_MCP", "1")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi import HTTPException

import genesis_router as gr
from db import exec_tasks_col, executives_col, genesis_pipelines_col, members_col, orgs_col

USER_ID = "genesis-test-user"


@pytest.fixture(autouse=True)
def clean():
    for col in (genesis_pipelines_col, orgs_col, members_col, executives_col, exec_tasks_col):
        col.delete_many({})
    yield


@pytest.fixture
def stubbed(monkeypatch):
    monkeypatch.setattr(gr, "extract_twin", lambda vision: {
        "twin": {
            "industry": "solar", "stage": "pre-revenue", "current_arr": 0, "currency": "₹",
            "team_size": 3, "runway_months": 12, "constraints": ["no sales team"],
            "fears": ["cash"], "strategic_forks": ["B2B vs B2C"],
            "founder_bottleneck": "sales", "what_they_have": ["distribution"],
        },
        "questions": ["Who is your first customer?", "What is your monthly burn?"],
    })
    monkeypatch.setattr(gr, "generate_mission", lambda twin, answers: {
        "mission": "Electrify every housing society in India", "north_star": "1M rooftops",
        "target": "₹100 crore ARR by 2029", "deadline": "2029",
        "priorities": ["Close 10 societies", "Hire 2 installers"],
        "decision_rules": "No install below 18% margin",
        "next_90_days_objective": "10 signed societies",
    })
    monkeypatch.setattr(gr, "generate_organization", lambda twin, mission: {
        "divisions": [
            {"name": "Sales", "function": "sales", "executives": [{
                "role": "VP Housing Society Sales", "department_function": "sales",
                "mission": "Sign 10 societies", "spending_limit_inr": 100000,
                "authority_level": "L3", "kpis": [{"name": "Signed", "target": "10", "weight": 10}],
                "knowledge_domains": ["solar", "sales"]}]},
            {"name": "Delivery", "function": "operations", "executives": [{
                "role": "Head of Installation", "department_function": "operations",
                "mission": "Install on time", "spending_limit_inr": 50000,
                "authority_level": "L3", "kpis": [{"name": "On-time", "target": "95%", "weight": 10}],
                "knowledge_domains": ["ops"]}]},
        ],
        "culture": [{"statement": "Owner mindset", "heuristic": "Fix before escalate",
                     "anti_pattern": "Blame", "weight": 8}],
    })
    monkeypatch.setattr(gr, "generate_tasks_for_executive",
                        lambda ex, mission: [{"description": f"{ex['role']} first task", "capability": "email"}])


def test_builder_pipeline_end_to_end(stubbed):
    user = {"id": USER_ID}

    start = gr.genesis_start(gr.StartIn(vision="Build India's largest rooftop solar company."), user=user)
    assert start["stage"] == "clarify"
    assert len(start["questions"]) == 2

    status = gr.genesis_status(user=user)
    assert status["twin"]["industry"] == "solar"
    assert status["questions"][0] == "Who is your first customer?"

    answer = gr.genesis_answer(gr.AnswerIn(answers={"0": "Housing societies"}), user=user)
    assert answer["stage"] == "review_mission"
    assert gr.genesis_status(user=user)["mission"]["target"] == "₹100 crore ARR by 2029"

    approved_mission = gr.genesis_approve_mission(gr.MissionApprovalIn(
        mission=answer["mission"], north_star="1M rooftops",
        target=answer["mission"]["target"], deadline="2029",
        priorities=answer["mission"]["priorities"], decision_rules="No install below 18% margin",
    ), user=user)
    assert approved_mission["stage"] == "review_org"
    assert len(approved_mission["organization"]["divisions"]) == 2
    assert approved_mission["capabilities_needed"]

    approved_org = gr.genesis_approve_org(gr.OrgApprovalIn(
        divisions=approved_mission["organization"]["divisions"],
        culture=approved_mission["organization"]["culture"],
    ), user=user)
    assert approved_org["stage"] == "connect_tools"
    assert approved_org["executives_created"] == 2
    assert orgs_col.find_one({"owner_user_id": USER_ID})["north_star"] == "1M rooftops"
    assert executives_col.count_documents({"org_id": approved_org["org_id"]}) == 2
    assert members_col.count_documents({"org_id": approved_org["org_id"], "role": "owner"}) == 1

    launched = gr.genesis_launch(user=user)
    assert launched["stage"] == "launched"
    assert launched["tasks_generated"] == 2
    assert exec_tasks_col.count_documents({"org_id": approved_org["org_id"]}) == 2

    status = gr.genesis_status(user=user)
    assert status["stage"] == "launched"
    assert status["org_id"] == approved_org["org_id"]
    assert len(status["executives"]) == 2
    assert status["tasks_generated"] == 2


def test_empty_org_design_is_blocked(stubbed, monkeypatch):
    user = {"id": "genesis-empty-user"}
    monkeypatch.setattr(gr, "generate_organization", lambda twin, mission: {"divisions": [], "culture": []})
    gr.genesis_start(gr.StartIn(vision="Build a solar company in India."), user=user)
    answer = gr.genesis_answer(gr.AnswerIn(answers={}), user=user)

    with pytest.raises(HTTPException) as exc:
        gr.genesis_approve_mission(gr.MissionApprovalIn(
            mission=answer["mission"], north_star="x", target="t", deadline="2029",
            priorities=[], decision_rules="r",
        ), user=user)
    assert exc.value.status_code == 422
    assert gr.genesis_status(user=user)["stage"] == "review_mission"
