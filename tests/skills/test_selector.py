from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from copal_cli.skills.registry import SkillMeta
from copal_cli.skills.selector import Selector


def make_skill(identifier: str, name: str, description: str, *tags: str) -> SkillMeta:
    return SkillMeta(
        identifier=identifier,
        name=name,
        description=description,
        tags=tags,
        origin="test",
        skill_path=Path(f"/skills/{identifier}"),
    )


def test_exact_match_search_returns_high_score() -> None:
    skills = [
        make_skill("greet", "Greeter", "Offers a friendly greeting", "communication"),
        make_skill("calc", "Calculator", "Performs arithmetic", "math"),
    ]
    selector = Selector(skills)

    results = selector.search("friendly greeting", k=2)

    assert results
    ids = [skill.identifier for skill, _ in results]
    assert ids[0] == "greet"
    assert results[0][1] > 0.5


def test_fuzzy_search_matches_close_terms() -> None:
    skills = [
        make_skill("sum", "Summer", "Adds numbers together", "math"),
        make_skill("chat", "Chat", "Engages in conversation", "communication"),
    ]
    selector = Selector(skills)

    results = selector.search("addition", k=2, threshold=0.2)

    assert results
    assert results[0][0].identifier == "sum"


def test_threshold_filters_low_scores() -> None:
    skills = [
        make_skill("sum", "Adder", "Adds numbers", "math"),
        make_skill("chat", "Chat", "Talks", "communication"),
    ]
    selector = Selector(skills)

    results = selector.search("math", k=5, threshold=0.5)

    assert all(score >= 0.5 for _, score in results)


def test_empty_query_returns_no_results() -> None:
    skills = [make_skill("sum", "Adder", "Adds numbers", "math")]
    selector = Selector(skills)

    assert selector.search("", k=5) == []
    assert selector.search("   ", k=5) == []
