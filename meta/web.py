# meta/web.py

from flask import Blueprint, render_template, abort, request, redirect, url_for, jsonify
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from uuid import uuid4
import subprocess
from datetime import datetime, timezone

from markupsafe import Markup

try:
    from werkzeug.utils import secure_filename
except ImportError:
    from werkzeug.security import secure_filename

try:
    from markdown import markdown as md
except ImportError:
    def md(text, **kwargs):
        return text

from meta.core import TICKETS_DIR

from meta.core import ROOT_DIR as BASE_DIR

USING_AI = False

# Blueprint – mounted at /meta - TEST DEPLOY!

'''
meta_bp = Blueprint(
    "meta",
    __name__,
    url_prefix="/meta",
    template_folder="../meta",  # assumes project_root/templates/...
)
'''

meta_bp = Blueprint(
    "meta",
    __name__,
    url_prefix="/meta",
    template_folder="templates",  # 👈 relative to the meta package
)


@meta_bp.app_template_filter("markdown")
def markdown_filter(text: str) -> Markup:
    """
    Render Markdown to safe HTML for templates.
    """
    if not text:
        return Markup("")
    html = md(
        text,
        extensions=["fenced_code", "tables", "sane_lists"],
        output_format="html5",
    )
    return Markup(html)


ALLOWED_EXTENSIONS = {".json"}  # 👈 only allow JSON uploads


def allowed_file(filename: str) -> bool:
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


# ----------------- helpers -----------------

from collections import defaultdict
from typing import DefaultDict, Tuple


def load_tickets_with_hierarchy(
        tickets: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], DefaultDict[str, List[Dict[str, Any]]]]:
    """
    Given a list of tickets, return:
      - top_level_tickets: tickets with no valid parent in this list
      - children_by_parent_id: map[parent_id] -> [child_ticket, ...]
    """

    if not tickets:
        return [], defaultdict(list)

    # Map of ticket_id -> ticket for quick lookup
    by_id: Dict[str, Dict[str, Any]] = {
        t.get("ticket_id", ""): t for t in tickets if t.get("ticket_id")
    }

    children_by_parent: DefaultDict[str, List[Dict[str, Any]]] = defaultdict(list)

    # assign children to parents (only within this filtered set)
    for t in tickets:
        parent_id = (t.get("parent_id") or "").strip()
        if parent_id and parent_id in by_id:
            children_by_parent[parent_id].append(t)

    # top-level tickets = those with no parent_id OR parent_id not found in this filtered set
    top_level: List[Dict[str, Any]] = []
    for t in tickets:
        parent_id = (t.get("parent_id") or "").strip()
        if not parent_id or parent_id not in by_id:
            top_level.append(t)

    # sorting helper
    def created_at_key(ticket: Dict[str, Any]) -> str:
        # adjust if you store created_at differently
        return ticket.get("created_at", "") or ""

    # parents: newest first
    top_level.sort(key=created_at_key, reverse=True)

    # children: oldest first under each parent
    for child_list in children_by_parent.values():
        child_list.sort(key=created_at_key)

    return top_level, children_by_parent


def generate_manual_ticket_id() -> str:
    """Generate a manual ticket_id like MANUAL-db3102a1."""
    return f"MANUAL-{uuid4().hex[:8]}"


def _load_ticket_file(path: Path) -> Dict[str, Any]:
    """Load a single ticket JSON file, tolerating errors and normalising fields."""
    try:
        with path.open("r", encoding="utf-8") as f:
            ticket = json.load(f)
    except Exception as e:
        ticket = {
            "ticket_id": path.stem,
            "title": f"[Failed to load: {e}]",
            "priority": "unknown",
            "status": "open",
        }

    # Ensure ticket_id exists
    ticket.setdefault("ticket_id", path.stem)

    # NORMALISATION LAYER for the UI:
    # - old schema uses: summary / acceptance_criteria
    # - real schema uses: description / evidence
    if "summary" not in ticket and "description" in ticket:
        ticket["summary"] = ticket["description"]

    if "acceptance_criteria" not in ticket and "evidence" in ticket:
        ticket["acceptance_criteria"] = ticket["evidence"]

    # And vice-versa (if a new ticket is created via UI with summary/acceptance_criteria)
    if "description" not in ticket and "summary" in ticket:
        ticket["description"] = ticket["summary"]

    if "evidence" not in ticket and "acceptance_criteria" in ticket:
        ticket["evidence"] = ticket["acceptance_criteria"]

    return ticket


def list_all_tickets() -> List[Dict[str, Any]]:
    """Return all ticket dicts sorted by ticket_id (desc)."""
    if not TICKETS_DIR.exists():
        return []

    tickets: List[Dict[str, Any]] = []
    for path in sorted(TICKETS_DIR.glob("*.json")):
        tickets.append(_load_ticket_file(path))

    # If ticket_id is date-based like 2025-11-28-10, this gives newest first
    tickets.sort(key=lambda t: t.get("ticket_id", ""), reverse=False)
    return tickets


def get_ticket_by_id(ticket_id: str) -> Optional[Dict[str, Any]]:
    """
    Look up a ticket by its ID.

    For now we assume filename is `{ticket_id}.json`.
    """
    candidate = TICKETS_DIR / f"{ticket_id}.json"
    if candidate.exists():
        return _load_ticket_file(candidate)

    # Fallback: scan all and match ticket_id field in case filenames differ
    for t in list_all_tickets():
        if t.get("ticket_id") == ticket_id:
            return t

    return None


# ----------------- routes -----------------

@meta_bp.route("/upload", methods=["GET"])
def upload_ticket_form():
    """Show the upload form."""
    return render_template("meta_upload.html")


@meta_bp.route("/upload", methods=["POST"])
def upload_ticket_post():
    # Grab all files for the input named "ticket_files"
    files = request.files.getlist("ticket_files")

    if not files:
        return render_template(
            "meta_upload.html",
            error="No files selected.",
            results=[],
        )

    results = []

    for f in files:
        filename = (f.filename or "").strip()
        if not filename:
            continue

        if not allowed_file(filename):
            results.append({
                "filename": filename,
                "status": "error",
                "message": "Only .json files are allowed.",
            })
            continue

        safe_name = secure_filename(filename)
        dest_path = TICKETS_DIR / safe_name

        try:
            # Read and validate JSON
            raw = f.read()
            data = json.loads(raw.decode("utf-8"))

            # Re-serialise nicely and save
            dest_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

            results.append({
                "filename": safe_name,
                "status": "ok",
                "message": f"Uploaded to {dest_path}",
            })
        except Exception as e:
            results.append({
                "filename": safe_name,
                "status": "error",
                "message": f"Failed to save: {e}",
            })

    return render_template(
        "meta_upload.html",
        error=None,
        results=results,
    )



@meta_bp.route("/<ticket_id>/run", methods=["POST"])
def run_ticket(ticket_id: str):
    """
    Fire off Bob/Chad to work this specific ticket_id.

    This is fire-and-forget: we spawn a subprocess that runs
    `python3 -m bob.meta self_cycle --ticket-id <ticket_id> --count 1`.
    """
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        abort(404)

    # Don't run closed tickets
    if ticket.get("status") == "done":
        return redirect(url_for("meta.meta_detail", ticket_id=ticket_id))

    # Optionally stamp a last_run_at field in the JSON
    ticket["last_run_at"] = datetime.now(timezone.utc).isoformat()
    path = TICKETS_DIR / f"{ticket_id}.json"
    if path.exists():
        with path.open("w", encoding="utf-8") as f:
            json.dump(ticket, f, indent=2)

    # Spawn Bob meta in the background
    # (BASE_DIR is your project root from earlier)
    try:
        subprocess.Popen(
            [
                "python3",
                "-m",
                "meta.core",
                "run_ticket",
                "--id",
                ticket_id,
                "--retries",
                "2",
            ],
            cwd=BASE_DIR,  # project root
        )
    except Exception as e:
        # You can log this properly if you want
        print(f"[meta_web] Failed to start self_cycle for {ticket_id}: {e}")

    return redirect(url_for("meta.meta_detail", ticket_id=ticket_id))


@meta_bp.route("/<ticket_id>/delete", methods=["POST"])
def delete_ticket(ticket_id):
    tickets_dir = TICKETS_DIR  # Path("data/meta/tickets") or similar
    ticket_path = tickets_dir / f"{ticket_id}.json"

    print(ticket_id)
    print(ticket_path)

    if ticket_path.exists():
        try:
            ticket_path.unlink()  # actually delete the ticket file
            # optionally: flash("Ticket deleted", "success")
        except Exception as e:
            # optionally: flash(f"Error deleting ticket: {e}", "error")
            pass

    # If it doesn't exist, just bounce back to index anyway
    return redirect(url_for("meta.meta_index") + "?status=all")


@meta_bp.route("/<ticket_id>/edit", methods=["GET", "POST"])
def edit_ticket(ticket_id: str):
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        abort(404)

    # Helper to keep behaviour consistent with new_ticket()
    def _split_lines(block: str) -> list[str]:
        return [
            line.strip("-• ").strip()
            for line in block.splitlines()
            if line.strip()
        ]

    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        area = (request.form.get("component") or "").strip()
        priority = (request.form.get("priority") or "medium").strip()
        summary = (request.form.get("summary") or "").strip()
        category = (request.form.get("category") or ticket.get("category") or "general").strip()
        acceptance_raw = request.form.get("acceptance_criteria") or ""
        steps_raw = request.form.get("suggested_steps") or ""
        safe_paths_raw = request.form.get("safe_paths") or ""
        kind = (request.form.get("kind") or "self_improvement").strip()
        parent_id = (request.form.get("parent_id") or "").strip() or None  # 👈 NEW

        if not title:
            # Re-render form with error + posted data
            form = dict(request.form)
            form.setdefault("safe_paths", safe_paths_raw)
            all_tickets = list_all_tickets()
            return render_template(
                "meta_new.html",  # reuse same template
                error="Title is required.",
                form=form,
                ticket=ticket,
                edit_mode=True,
                using_ai=USING_AI,
                all_tickets=all_tickets,
            )

        evidence = _split_lines(acceptance_raw)
        suggested_steps = _split_lines(steps_raw)
        safe_paths = [
            line.strip().lstrip("-• ").strip()
            for line in safe_paths_raw.splitlines()
            if line.strip()
        ]

        # Update fields on the existing ticket dict
        ticket["title"] = title
        ticket["area"] = area or ticket.get("area", "general")
        ticket["priority"] = priority
        ticket["description"] = summary or title
        ticket["summary"] = summary or title
        ticket["evidence"] = evidence
        ticket["acceptance_criteria"] = evidence
        ticket["suggested_steps"] = suggested_steps
        ticket["safe_paths"] = safe_paths
        ticket["kind"] = kind
        ticket["category"] = category

        # parent relationship
        if parent_id:
            ticket["parent_id"] = parent_id
        else:
            ticket.pop("parent_id", None)  # remove if cleared

        # Keep id/ticket_id/created_at/kind/status as-is
        path = TICKETS_DIR / f"{ticket_id}.json"
        TICKETS_DIR.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(ticket, f, indent=2)

        return redirect(url_for("meta.meta_detail", ticket_id=ticket_id))

    # GET: pre-populate form from existing ticket
    form = {
        "title": ticket.get("title", ""),
        "component": ticket.get("area", ""),
        "priority": ticket.get("priority", "medium"),
        "summary": ticket.get("summary") or ticket.get("description", ""),
        "acceptance_criteria": "\n".join(ticket.get("evidence") or []),
        "suggested_steps": "\n".join(ticket.get("suggested_steps") or []),
        "safe_paths": "\n".join(ticket.get("safe_paths") or []),
        "kind": ticket.get("kind", ""),
        "category": ticket.get("category", ""),
        "parent_id": ticket.get("parent_id", ""),  # 👈 so template can preselect
    }

    # All tickets for the parent dropdown (template hides self)
    all_tickets = list_all_tickets()

    return render_template(
        "meta_new.html",  # reuse same template
        error=None,
        form=form,
        ticket=ticket,
        edit_mode=True,
        using_ai=USING_AI,
        all_tickets=all_tickets,
    )


@meta_bp.route("/new", methods=["GET", "POST"])
def new_ticket():
    if request.method == "POST":
        title = (request.form.get("title") or "").strip()
        area = (request.form.get("component") or "").strip()  # map component -> area
        priority = (request.form.get("priority") or "medium").strip()
        summary = (request.form.get("summary") or "").strip()
        category = (request.form.get("category") or "general").strip()
        acceptance_raw = request.form.get("acceptance_criteria") or ""
        steps_raw = request.form.get("suggested_steps") or ""
        parent_id = (request.form.get("parent_id") or "").strip() or None  # 👈 NEW

        if not title:
            all_tickets = list_all_tickets()
            return render_template(
                "meta_new.html",
                error="Title is required.",
                form=request.form,
                using_ai=USING_AI,
                all_tickets=all_tickets,
                ticket=None,
                edit_mode=False,
            )

        def _split_lines(block: str) -> list[str]:
            return [
                line.strip("-• ").strip()
                for line in block.splitlines()
                if line.strip()
            ]

        evidence = _split_lines(acceptance_raw)

        now = datetime.now(timezone.utc)
        created_at = now.isoformat()
        # compact id like 2025-12-01-214215
        id_str = now.strftime("%Y-%m-%d-%H%M%S")
        ticket_id = generate_manual_ticket_id()
        raw_issue_key = f"manual:{id_str}"
        kind = (request.form.get("kind") or "self_improvement").strip()

        safe_paths_raw = request.form.get("safe_paths") or ""
        safe_paths = [
            line.strip().lstrip("-• ").strip()
            for line in safe_paths_raw.splitlines()
            if line.strip()
        ]

        ticket: Dict[str, Any] = {
            "id": id_str,
            "scope": "self",
            "area": area or "general",
            "title": title,
            "description": summary or title,
            "evidence": evidence,
            "priority": priority,
            "created_at": created_at,
            "safe_paths": safe_paths,
            "raw_issue_key": raw_issue_key,
            "ticket_id": ticket_id,
            "status": "open",
            "kind": kind,
            "summary": summary or title,
            "acceptance_criteria": evidence,
            "suggested_steps": _split_lines(steps_raw),
            "last_run": None,
            "last_bob_reply": None,
            "last_chad_summary": None,
            "category": category,  # existing
        }

        if parent_id:
            ticket["parent_id"] = parent_id  # 👈 NEW

        TICKETS_DIR.mkdir(parents=True, exist_ok=True)
        path = TICKETS_DIR / f"{ticket_id}.json"
        with path.open("w", encoding="utf-8") as f:
            json.dump(ticket, f, indent=2)

        return redirect(url_for("meta.meta_detail", ticket_id=ticket_id))

    # GET
    all_tickets = list_all_tickets()
    return render_template(
        "meta_new.html",
        error=None,
        form={},
        using_ai=USING_AI,
        all_tickets=all_tickets,
        ticket=None,
        edit_mode=False,
    )


@meta_bp.route("/")
def meta_index():
    """
    Index page listing meta tickets, with optional status + category filter.
    /meta?status=open|done|all&category=foo|all

    Now rendered as:
      PARENT
          child
          child
      NEXT PARENT
          child
    """

    status = request.args.get("status", "open")  # default: open
    category = request.args.get("category", "all")

    # Load all tickets once (for filtering + categories)
    all_tickets = list_all_tickets()

    # Build list of available categories from ALL tickets (even if filtered out)
    categories = sorted(
        {
            t.get("category")
            for t in all_tickets
            if t.get("category")
        }
    )

    # Start from all tickets, then apply filters
    tickets = all_tickets

    # Filter by status
    if status in {"open", "done"}:
        tickets = [
            t for t in tickets
            if (t.get("status") or "open") == status
        ]

    # Filter by category (skip if "all")
    if category != "all":
        tickets = [
            t for t in tickets
            if t.get("category") == category
        ]

    # Build parent/child structure from the FILTERED tickets
    top_level, children_by_parent = load_tickets_with_hierarchy(tickets)

    return render_template(
        "meta_index.html",
        tickets=top_level,  # 👈 only parents / top-level
        children_by_parent=children_by_parent,  # 👈 mapping parent_id -> [children]
        current_status=status,
        current_category=category,
        categories=categories,
    )


@meta_bp.route("/<ticket_id>")
def meta_detail(ticket_id: str):
    """Detail page for a single ticket."""
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        abort(404)
    return render_template("meta_detail.html", ticket=ticket)


@meta_bp.route("/<ticket_id>/complete", methods=["POST"])
def mark_ticket_complete(ticket_id: str):
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        abort(404)

    # Update status
    ticket["status"] = "done"

    # Write updated JSON
    path = TICKETS_DIR / f"{ticket_id}.json"
    if path.exists():
        with path.open("w", encoding="utf-8") as f:
            json.dump(ticket, f, indent=2)

    return redirect(url_for("meta.meta_detail", ticket_id=ticket_id))


@meta_bp.route("/<ticket_id>/reopen", methods=["POST"])
def reopen_ticket(ticket_id: str):
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        abort(404)

    ticket["status"] = "open"

    path = TICKETS_DIR / f"{ticket_id}.json"
    if path.exists():
        with path.open("w", encoding="utf-8") as f:
            json.dump(ticket, f, indent=2)

    return redirect(url_for("meta.meta_detail", ticket_id=ticket_id))
