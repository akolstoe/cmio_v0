from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)


# --- Mock data -------------------------------------------------------------
users = {
    1: {"name": "Alex Caseworker"},
    2: {"name": "Jordan RN"},
}

clients = {
    1: {"name": "Sam Rivera"},
    2: {"name": "Lee Chen"},
}

messages = [
    {
        "id": 1,
        "type": "channel",
        "sender": users[1]["name"],
        "channel": "housing-support",
        "client": clients[1]["name"],
        "summary": "Visited housing office with Sam yesterday — application submitted.",
    },
    {
        "id": 2,
        "type": "direct",
        "sender": users[2]["name"],
        "channel": None,
        "client": clients[2]["name"],
        "summary": "Called pharmacy for Lee; refill ready Friday at 2pm.",
    },
]

pending_facts: List[Dict] = [
    {
        "id": 1,
        "client": clients[1]["name"],
        "value": "Housing application submitted",
        "security": "shared",
        "source_message": 1,
        "status": "pending",
    },
    {
        "id": 2,
        "client": clients[2]["name"],
        "value": "Pharmacy pickup Friday 2pm",
        "security": "sensitive",
        "source_message": 2,
        "status": "pending",
    },
]

encounter_notes: List[Dict] = [
    {
        "id": 1,
        "client": clients[1]["name"],
        "status": "draft",
        "summary": "Visited housing office with client",
        "details": "Draft created from channel post.",
        "created_at": datetime.utcnow(),
    },
    {
        "id": 2,
        "client": clients[2]["name"],
        "status": "ready_for_approval",
        "summary": "Called pharmacy on client's behalf",
        "details": "Pickup confirmed for Friday.",
        "created_at": datetime.utcnow(),
    },
]

case_notes: List[Dict] = []

tasks: List[Dict] = [
    {
        "id": 1,
        "title": "Prep SNAP application",
        "client": clients[1]["name"],
        "estimate": 25,
        "steps": [
            {"label": "Gather paystubs", "done": False},
            {"label": "Confirm residency doc", "done": False},
        ],
    },
    {
        "id": 2,
        "title": "Schedule follow-up call",
        "client": clients[2]["name"],
        "estimate": 10,
        "steps": [
            {"label": "Check pharmacy schedule", "done": True},
            {"label": "Text client reminder", "done": False},
        ],
    },
]

model_options = [
    {"id": "pattern", "label": "Pattern/Regex (fast)", "latency": "<1s"},
    {"id": "local-llm", "label": "Local LLM (balanced)", "latency": "~4s"},
    {"id": "private-llm", "label": "Private LLM (deep)", "latency": "~8s"},
]
selected_model = "pattern"


# --- Helpers ---------------------------------------------------------------

def get_stats():
    return {
        "pending_facts": len([f for f in pending_facts if f["status"] == "pending"]),
        "draft_notes": len([n for n in encounter_notes if n["status"] != "approved"]),
        "open_tasks": len(tasks),
    }


# --- Routes ----------------------------------------------------------------


@app.route("/")
def dashboard():
    stats = get_stats()
    return render_template(
        "dashboard.html",
        stats=stats,
        pending_facts=pending_facts,
        encounter_notes=encounter_notes,
        case_notes=case_notes,
        tasks=tasks,
        messages=messages,
        model_options=model_options,
        selected_model=selected_model,
    )


@app.post("/pending-facts/<int:fact_id>/<action>")
def update_fact(fact_id: int, action: str):
    for fact in pending_facts:
        if fact["id"] == fact_id:
            if action == "approve":
                fact["status"] = "approved"
            elif action == "reject":
                fact["status"] = "rejected"
            break
    return redirect(url_for("dashboard"))


@app.post("/notes/<int:note_id>/promote")
def promote_note(note_id: int):
    for note in encounter_notes:
        if note["id"] == note_id:
            note["status"] = "approved"
            case_notes.append(
                {
                    "id": len(case_notes) + 1,
                    "client": note["client"],
                    "body": note["details"],
                    "finalized_at": datetime.utcnow(),
                }
            )
            break
    return redirect(url_for("dashboard"))


@app.post("/model/select")
def select_model():
    global selected_model
    selected_model = request.form.get("model", selected_model)
    return redirect(url_for("dashboard"))


@app.post("/tasks/<int:task_id>/steps/<int:step_index>/toggle")
def toggle_step(task_id: int, step_index: int):
    for task in tasks:
        if task["id"] == task_id and 0 <= step_index < len(task["steps"]):
            task["steps"][step_index]["done"] = not task["steps"][step_index]["done"]
            break
    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
