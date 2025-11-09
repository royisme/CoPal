"""Handlers for skill related CLI commands."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .executor import SkillExecutor
from .registry import SkillRegistry, SkillRegistryBuilder
from .scaffold import SkillScaffolder
from .selector import SkillSelector

logger = logging.getLogger(__name__)

_DEFAULT_ROOT = Path(".copal/skills")


def _resolve_root(path: str | None) -> Path:
    root = Path(path or _DEFAULT_ROOT)
    return root


def _load_registry(root: Path) -> SkillRegistry:
    try:
        return SkillRegistry.from_index(root)
    except FileNotFoundError:
        builder = SkillRegistryBuilder(skills_root=root)
        registry = builder.build()
        registry.write_index()
        return registry


def registry_build_command(args: argparse.Namespace) -> int:
    root = _resolve_root(getattr(args, "skills_root", None))
    builder = SkillRegistryBuilder(skills_root=root)
    registry = builder.build_and_write()
    logger.info("Built registry with %d skill(s) at %s", len(registry.skills), root)
    return 0


def registry_list_command(args: argparse.Namespace) -> int:
    root = _resolve_root(getattr(args, "skills_root", None))
    language = getattr(args, "lang", None)
    registry = _load_registry(root)
    matches = registry.list(language=language)
    if not matches:
        logger.info("No skills found in registry at %s", root)
        return 1
    for skill in matches:
        line = f"{skill.name} [{skill.language}] - {skill.description}"
        print(line)
    return 0


def search_command(args: argparse.Namespace) -> int:
    root = _resolve_root(getattr(args, "skills_root", None))
    language = getattr(args, "lang", None)
    query = getattr(args, "query", "")
    if not query:
        logger.error("--query is required for search")
        return 1
    registry = _load_registry(root)
    selector = SkillSelector(registry.skills)
    matches = selector.search(query, language=language)
    if not matches:
        logger.info("No skills matched query '%s'", query)
        return 1
    for match in matches:
        skill = match.skill
        header = f"{skill.name} [{skill.language}] - {skill.description}"
        print(header)
        if skill.prelude:
            print(skill.prelude)
        print()
    return 0


def scaffold_command(args: argparse.Namespace) -> int:
    root = _resolve_root(getattr(args, "skills_root", None))
    name = args.name
    language = getattr(args, "lang", "python")
    description = getattr(args, "description", None)
    scaffolder = SkillScaffolder(skills_root=root)
    try:
        created = scaffolder.create(name, language=language, description=description)
    except FileExistsError as exc:
        logger.error(str(exc))
        return 1
    logger.info("Created skill scaffold at %s", created)
    return 0


def exec_command(args: argparse.Namespace) -> int:
    root = _resolve_root(getattr(args, "skills_root", None))
    skill_name = getattr(args, "skill", None)
    if not skill_name:
        logger.error("--skill is required for execution")
        return 1
    language = getattr(args, "lang", None)
    sandbox = getattr(args, "sandbox", False)
    registry = _load_registry(root)
    try:
        skill = registry.get(skill_name)
    except KeyError:
        logger.error("Skill '%s' not found in registry", skill_name)
        return 1
    if language and skill.language != language:
        logger.error(
            "Skill '%s' language mismatch (expected %s, got %s)",
            skill_name,
            language,
            skill.language,
        )
        return 1
    executor = SkillExecutor(stream=sys.stdout)
    try:
        executor.execute(skill, sandbox=sandbox)
    except PermissionError as exc:
        logger.error(str(exc))
        return 1
    except FileNotFoundError as exc:
        logger.error("Entrypoint missing for skill '%s': %s", skill_name, exc)
        return 1
    return 0
