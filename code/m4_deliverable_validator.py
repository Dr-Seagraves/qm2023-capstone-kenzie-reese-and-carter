"""
Milestone 4 deliverable validator.

This script converts the Milestone 4 instructions into structured Python data
and runs automated checks for required submission artifacts.

Usage examples:
    python3 code/m4_deliverable_validator.py
    python3 code/m4_deliverable_validator.py --root .
    python3 code/m4_deliverable_validator.py --team-members Kenzie Reese Carter
    python3 code/m4_deliverable_validator.py --json
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class RubricComponent:
    """A grading rubric component and its assigned points."""

    name: str
    points: int
    criteria: str


@dataclass(frozen=True)
class ChecklistItem:
    """A milestone checklist line item."""

    section: str
    description: str
    automatable: bool = False


@dataclass(frozen=True)
class DeliverableRequirement:
    """A file-based deliverable requirement that can be validated."""

    requirement_id: str
    description: str
    patterns: tuple[str, ...]
    min_count: int = 1
    max_count: Optional[int] = None
    page_min: Optional[int] = None
    page_max: Optional[int] = None


@dataclass
class ValidationFinding:
    """Result for one validation step."""

    requirement_id: str
    description: str
    status: str
    message: str
    matched_files: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Milestone4Spec:
    """Structured M4 specification from the assignment instructions."""

    rubric: tuple[RubricComponent, ...]
    checklists: tuple[ChecklistItem, ...]
    deliverables: tuple[DeliverableRequirement, ...]


def build_m4_spec() -> Milestone4Spec:
    """Create structured Milestone 4 rubric, checklist, and deliverable specs."""

    rubric = (
        RubricComponent(
            name="Team Memo: Reproducibility and Rigor",
            points=10,
            criteria="M1-M3 repo runs end-to-end; memo tables/figures match code; sound diagnostics.",
        ),
        RubricComponent(
            name="Team Memo: Structure and Clarity",
            points=10,
            criteria="Required sections present, organized, professional, and jargon-free.",
        ),
        RubricComponent(
            name="Team Memo: Results and Interpretation",
            points=12,
            criteria="Publication-ready tables/figures with clear economic interpretation.",
        ),
        RubricComponent(
            name="Team Memo: Recommendations and Caveats",
            points=8,
            criteria="Actionable recommendations with honest limitations and risk discussion.",
        ),
        RubricComponent(
            name="Individual Addendum",
            points=10,
            criteria="Specific contribution, defended decision, key limitation, and honesty.",
        ),
    )

    checklists = (
        ChecklistItem("Team Memo Checklist", "All required sections present", automatable=False),
        ChecklistItem("Team Memo Checklist", "Length is 5-7 pages", automatable=True),
        ChecklistItem("Team Memo Checklist", "Tables are formatted, not raw console output", automatable=False),
        ChecklistItem("Team Memo Checklist", "Figures are high resolution", automatable=False),
        ChecklistItem("Team Memo Checklist", "No jargon or unexplained acronyms", automatable=False),
        ChecklistItem("Team Memo Checklist", "Investment recommendations are specific", automatable=False),
        ChecklistItem("Team Memo Checklist", "Limitations and caveats are honest", automatable=False),
        ChecklistItem("Individual Addendum Checklist", "Personal contribution is specific", automatable=False),
        ChecklistItem("Individual Addendum Checklist", "Defended decision uses evidence", automatable=False),
        ChecklistItem("Individual Addendum Checklist", "Key limitation is substantive", automatable=False),
        ChecklistItem("Individual Addendum Checklist", "Length is exactly 1 page", automatable=True),
        ChecklistItem("Final Quality Check", "Team member names on both memo and addendum", automatable=False),
        ChecklistItem("Final Quality Check", "Submitted as PDFs", automatable=True),
        ChecklistItem("Final Quality Check", "Memo includes AI Audit appendix", automatable=False),
    )

    deliverables = (
        DeliverableRequirement(
            requirement_id="TEAM_MEMO_FILE",
            description="Team memo PDF exists (Final_Investment_Memo.pdf)",
            patterns=(
                "Final_Investment_Memo.pdf",
                "final_investment_memo.pdf",
                "*final*investment*memo*.pdf",
            ),
            min_count=1,
            page_min=5,
            page_max=7,
        ),
        DeliverableRequirement(
            requirement_id="INDIVIDUAL_ADDENDA_FILES",
            description="At least one Individual_Addendum_[Name].pdf exists",
            patterns=(
                "Individual_Addendum_*.pdf",
                "individual_addendum_*.pdf",
            ),
            min_count=1,
            page_min=1,
            page_max=1,
        ),
    )

    return Milestone4Spec(rubric=rubric, checklists=checklists, deliverables=deliverables)


def _normalize_token(value: str) -> str:
    """Normalize strings for tolerant filename matching."""

    return re.sub(r"[^a-z0-9]", "", value.lower())


def _path_matches_patterns(path: Path, patterns: tuple[str, ...]) -> bool:
    """Match a path against shell-style patterns using case-insensitive checks."""

    rel_text = path.as_posix().lower()
    name_text = path.name.lower()

    for pattern in patterns:
        p = pattern.lower()
        if fnmatch.fnmatch(name_text, p) or fnmatch.fnmatch(rel_text, p):
            return True
    return False


def find_matching_files(root: Path, patterns: tuple[str, ...]) -> list[Path]:
    """Return sorted files under root matching one of the provided patterns."""

    ignore_dirs = {
        ".git",
        ".venv",
        ".mypy_cache",
        ".pytest_cache",
        "__pycache__",
        ".ipynb_checkpoints",
        "node_modules",
        "venv",
    }

    matches: list[Path] = []
    for current_dir, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]

        current_path = Path(current_dir)
        for filename in filenames:
            path = current_path / filename
            rel_path = path.relative_to(root)
            if _path_matches_patterns(rel_path, patterns):
                matches.append(path)

    # De-duplicate and sort by relative path for stable output.
    unique = sorted({m.resolve() for m in matches})
    return [Path(p) for p in unique]


def get_pdf_page_count(pdf_path: Path) -> Optional[int]:
    """Get PDF page count using an installed reader; return None when unavailable."""

    # Try pypdf first (if installed in environment).
    try:
        from pypdf import PdfReader  # type: ignore

        reader = PdfReader(str(pdf_path))
        return len(reader.pages)
    except Exception:
        pass

    # Fallback for environments with PyPDF2.
    try:
        from PyPDF2 import PdfReader as PdfReader2  # type: ignore

        reader = PdfReader2(str(pdf_path))
        return len(reader.pages)
    except Exception:
        pass

    # Fallback to the external `pdfinfo` command.
    try:
        completed = subprocess.run(
            ["pdfinfo", str(pdf_path)],
            check=False,
            capture_output=True,
            text=True,
        )
        if completed.returncode == 0:
            match = re.search(r"^Pages:\s+(\d+)\s*$", completed.stdout, flags=re.MULTILINE)
            if match:
                return int(match.group(1))
    except FileNotFoundError:
        return None

    return None


def validate_deliverables(spec: Milestone4Spec, root: Path) -> list[ValidationFinding]:
    """Run file-based checks encoded in the spec."""

    findings: list[ValidationFinding] = []

    for requirement in spec.deliverables:
        matches = find_matching_files(root, requirement.patterns)
        rel_matches = [str(path.relative_to(root)) for path in matches]

        if len(matches) < requirement.min_count:
            findings.append(
                ValidationFinding(
                    requirement_id=requirement.requirement_id,
                    description=requirement.description,
                    status="FAIL",
                    message=(
                        f"Found {len(matches)} file(s), but at least {requirement.min_count} "
                        "are required."
                    ),
                    matched_files=rel_matches,
                )
            )
            continue

        if requirement.max_count is not None and len(matches) > requirement.max_count:
            findings.append(
                ValidationFinding(
                    requirement_id=requirement.requirement_id,
                    description=requirement.description,
                    status="FAIL",
                    message=(
                        f"Found {len(matches)} file(s), but at most {requirement.max_count} "
                        "are allowed."
                    ),
                    matched_files=rel_matches,
                )
            )
            continue

        findings.append(
            ValidationFinding(
                requirement_id=requirement.requirement_id,
                description=requirement.description,
                status="PASS",
                message=f"Found {len(matches)} required file(s).",
                matched_files=rel_matches,
            )
        )

        # Page checks are done per matched PDF when requested.
        if requirement.page_min is not None or requirement.page_max is not None:
            for path in matches:
                pages = get_pdf_page_count(path)
                rel_path = str(path.relative_to(root))
                file_tag = f"{requirement.requirement_id}_PAGES"

                if pages is None:
                    findings.append(
                        ValidationFinding(
                            requirement_id=file_tag,
                            description=f"Page count for {rel_path}",
                            status="WARN",
                            message=(
                                "Could not determine page count (install pypdf/PyPDF2 or pdfinfo)."
                            ),
                            matched_files=[rel_path],
                        )
                    )
                    continue

                low_ok = requirement.page_min is None or pages >= requirement.page_min
                high_ok = requirement.page_max is None or pages <= requirement.page_max
                in_range = low_ok and high_ok

                if in_range:
                    findings.append(
                        ValidationFinding(
                            requirement_id=file_tag,
                            description=f"Page count for {rel_path}",
                            status="PASS",
                            message=(
                                f"{pages} page(s), expected range "
                                f"{requirement.page_min}-{requirement.page_max}."
                            ),
                            matched_files=[rel_path],
                        )
                    )
                else:
                    findings.append(
                        ValidationFinding(
                            requirement_id=file_tag,
                            description=f"Page count for {rel_path}",
                            status="FAIL",
                            message=(
                                f"{pages} page(s), expected range "
                                f"{requirement.page_min}-{requirement.page_max}."
                            ),
                            matched_files=[rel_path],
                        )
                    )

    return findings


def validate_team_member_addenda(
    root: Path,
    findings: list[ValidationFinding],
    team_members: list[str],
) -> None:
    """Check that each named team member has a matching individual addendum PDF."""

    addenda_files = find_matching_files(root, ("Individual_Addendum_*.pdf", "individual_addendum_*.pdf"))
    normalized_map = {
        path: _normalize_token(path.stem.replace("individualaddendum", ""))
        for path in addenda_files
    }

    for member in team_members:
        target = _normalize_token(member)
        matched = [path for path, token in normalized_map.items() if target and target in token]

        if matched:
            findings.append(
                ValidationFinding(
                    requirement_id="INDIVIDUAL_ADDENDUM_MEMBER_MATCH",
                    description=f"Individual addendum exists for {member}",
                    status="PASS",
                    message=f"Found {len(matched)} matching addendum file(s).",
                    matched_files=[str(p.relative_to(root)) for p in matched],
                )
            )
        else:
            findings.append(
                ValidationFinding(
                    requirement_id="INDIVIDUAL_ADDENDUM_MEMBER_MATCH",
                    description=f"Individual addendum exists for {member}",
                    status="FAIL",
                    message="No matching addendum filename found for this team member.",
                    matched_files=[],
                )
            )


def build_manual_review_items(spec: Milestone4Spec) -> list[ChecklistItem]:
    """Return checklist items that require human review."""

    return [item for item in spec.checklists if not item.automatable]


def summarize(findings: list[ValidationFinding]) -> dict[str, int]:
    """Count PASS/FAIL/WARN findings."""

    summary = {"PASS": 0, "FAIL": 0, "WARN": 0}
    for finding in findings:
        summary[finding.status] = summary.get(finding.status, 0) + 1
    return summary


def print_report(
    root: Path,
    spec: Milestone4Spec,
    findings: list[ValidationFinding],
    manual_items: list[ChecklistItem],
) -> None:
    """Print human-readable validation report."""

    print("=" * 72)
    print("Milestone 4 Deliverable Validation Report")
    print("=" * 72)
    print(f"Repository root: {root}")
    print()

    print("Rubric (Structured Data)")
    for component in spec.rubric:
        print(f"- {component.name}: {component.points} points")
    print()

    print("Automated Checks")
    for finding in findings:
        print(f"[{finding.status}] {finding.requirement_id}: {finding.description}")
        print(f"  {finding.message}")
        if finding.matched_files:
            print("  Files:")
            for rel in finding.matched_files:
                print(f"  - {rel}")
    print()

    print("Manual Review Checklist")
    for item in manual_items:
        print(f"[ ] {item.section}: {item.description}")
    print()

    score = summarize(findings)
    print("Summary")
    print(f"- PASS: {score['PASS']}")
    print(f"- FAIL: {score['FAIL']}")
    print(f"- WARN: {score['WARN']}")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""

    parser = argparse.ArgumentParser(
        description="Validate Milestone 4 capstone deliverables using a structured rubric/checklist.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Repository root to validate (default: current directory).",
    )
    parser.add_argument(
        "--team-members",
        nargs="*",
        default=[],
        help="Optional team member names to verify Individual_Addendum_[Name].pdf coverage.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output report as JSON instead of plain text.",
    )
    return parser.parse_args()


def main() -> int:
    """Entry point."""

    args = parse_args()
    root = Path(args.root).resolve()

    if not root.exists() or not root.is_dir():
        print(f"Error: root directory not found: {root}")
        return 2

    spec = build_m4_spec()
    findings = validate_deliverables(spec, root)

    if args.team_members:
        validate_team_member_addenda(root, findings, args.team_members)

    manual_items = build_manual_review_items(spec)

    if args.json:
        payload = {
            "root": str(root),
            "rubric": [asdict(component) for component in spec.rubric],
            "automated_findings": [asdict(finding) for finding in findings],
            "manual_review_items": [asdict(item) for item in manual_items],
            "summary": summarize(findings),
        }
        print(json.dumps(payload, indent=2))
    else:
        print_report(root, spec, findings, manual_items)

    # Return non-zero when automated checks include failures.
    failed = any(f.status == "FAIL" for f in findings)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
