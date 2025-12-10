from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import List

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn

from copal_cli.fs.writer import atomic_write

logger = logging.getLogger(__name__)
console = Console()


INIT_TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "init"
PACKS_TEMPLATE_DIR = Path(__file__).parent.parent / "templates" / "packs"

def init_command(target: str = ".", force: bool = False, dry_run: bool = False, tools: List[str] = None, packs: List[str] = None) -> int:
    """Initialize a new Copal project."""
    target_path = Path(target).resolve()
    
    # Welcome
    console.print(Panel.fit(
        "[bold blue]Copal[/bold blue] - Agent Harness Configuration",
        subtitle="v0.1.0"
    ))

    # Interactive selection (if not provided)
    if tools is None:
        console.print("\n[bold]Select AI Adapters[/bold] (supported: claude, codex, gemini)")
        tool_input = Prompt.ask("Enter adapters separated by comma", default="claude")
        tools = [t.strip() for t in tool_input.split(",") if t.strip()]
        
        # Validate tools
        valid_tools = {"claude", "codex", "gemini"}
        invalid = [t for t in tools if t not in valid_tools]
        if invalid:
            console.print(f"[yellow]Warning: Ignoring unknown adapters: {', '.join(invalid)}[/yellow]")
            tools = [t for t in tools if t in valid_tools]
            if not tools:
                console.print("[red]No valid adapters selected. Defaulting to claude.[/red]")
                tools = ["claude"]

    default_pack = "engineering_loop"
    valid_packs = ["engineering_loop"]
    
    if packs is None:
        console.print("\n[bold]Select Packs[/bold] (available: engineering_loop)")
        pack_input = Prompt.ask("Enter packs separated by comma", default="engineering_loop")
        packs = [p.strip() for p in pack_input.split(",") if p.strip()]
        
        # Validate packs
        invalid_packs = [p for p in packs if p not in valid_packs]
        if invalid_packs:
            console.print(f"[yellow]Warning: Ignoring unknown packs: {', '.join(invalid_packs)}[/yellow]")
            packs = [p for p in packs if p in valid_packs]
            if not packs:
                 packs = ["engineering_loop"]
    
    if dry_run:
        console.print("[yellow]Dry run mode enabled. No files will be written.[/yellow]")

    # Create structure
    copal_dir = target_path / ".copal"
    
    steps = [
        ("Creating directory structure", lambda: _create_structure(copal_dir, dry_run)),
        ("Generating manifest.yaml", lambda: _generate_manifest(target_path, tools, packs, default_pack, force, dry_run)),
        ("Generating AGENTS.md & UserAgents.md", lambda: _create_base_files(target_path, force, dry_run)),
        ("Installing hooks", lambda: _install_hooks(copal_dir, force, dry_run)),
        ("Installing global knowledge base", lambda: _install_global_knowledge(copal_dir, force, dry_run)),
        ("Installing packs", lambda: _install_packs(packs, copal_dir, force, dry_run)),
        ("Initializing Memory Layer", lambda: _init_memory(copal_dir, force, dry_run)),
        ("Creating documentation structure", lambda: _install_docs(copal_dir, force, dry_run)),
    ]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        for desc, func in steps:
            task = progress.add_task(desc, total=1)
            try:
                func()
                progress.update(task, completed=1)
            except Exception as e:
                console.print(f"[red]Error during {desc}: {e}[/red]")
                # In debug mode broadly, we might want traceback. For now, just log.
                logger.exception("Init failed")
                return 1

    console.print(f"\n[green]✓ Copal initialized in {target_path}[/green]")
    console.print("\nNext steps:")
    console.print("  1. Review [cyan]AGENTS.md[/cyan] and [cyan]UserAgents.md[/cyan]")
    console.print("  2. Check [cyan].copal/manifest.yaml[/cyan]")
    console.print("  3. Run [bold]copal export [tool][/bold] to generate tool configs")
    
    return 0

def _create_structure(copal_dir: Path, dry_run: bool):
    if not dry_run:
        copal_dir.mkdir(parents=True, exist_ok=True)
        
        artifacts_dir = copal_dir / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)
        (artifacts_dir / ".gitkeep").touch()

        runtime_dir = copal_dir / "runtime"
        runtime_dir.mkdir(exist_ok=True) # Generated prompts go here
        (runtime_dir / ".gitkeep").touch()

def _generate_manifest(target_path: Path, tools: List[str], packs: List[str], default_pack: str, force: bool, dry_run: bool):
    dst = target_path / ".copal" / "manifest.yaml"
    
    if dry_run: return

    if dst.exists() and not force:
        logger.warning(f"Skipping {dst} (exists)")
        return

    # Use default_pack's verify script if available
    verify_cmd = f".copal/packs/{default_pack}/scripts/verify.sh" if default_pack in packs else "echo 'No verify script'"

    manifest_content = f"""version: "0.1.0"
project:
  name: {target_path.name}
  description: "Project initialized with Copal"
default_pack: {default_pack}

# Active packs for this project
packs:
"""
    for p in packs:
        manifest_content += f"  - {p}\n"

    manifest_content += f"""
# Enabled AI adapters
adapters:
"""
    for t in tools:
        manifest_content += f"  - {t}\n"

    manifest_content += f"""
# Verification command (Agent runs this to verify work)
verify:
  command: {verify_cmd}

# Memory configuration
memory:
  enabled: true
  provider: json
"""
    
    atomic_write(dst, manifest_content, overwrite=force)

def _install_hooks(copal_dir: Path, force: bool, dry_run: bool):
    if dry_run: return
    
    src = INIT_TEMPLATE_DIR / ".copal" / "hooks"
    dst = copal_dir / "hooks"
    
    if not src.exists():
        # Ideally this should be a warning, but might be too noisy if hooks are optional
        # logger.warning(f"Hooks template not found at {src}")
        return

    if dst.exists():
        if force:
            shutil.rmtree(dst)
        else:
            logger.warning("Hooks already installed")
            return
            
    shutil.copytree(src, dst)

def _install_global_knowledge(copal_dir: Path, force: bool, dry_run: bool):
    """Install global knowledge base from init template."""
    if dry_run: return
    
    src = INIT_TEMPLATE_DIR / ".copal" / "global"
    dst = copal_dir / "global"
    
    if not src.exists():
        logger.warning(f"Global knowledge base template not found at {src}")
        return

    if dst.exists():
        if force:
            shutil.rmtree(dst)
        else:
            logger.warning("Global knowledge base already installed")
            return
            
    shutil.copytree(src, dst)
    logger.info(f"Installed global knowledge base to {dst}")

def _create_base_files(target_path: Path, force: bool, dry_run: bool):
    if dry_run: return
    
    for filename in ["AGENTS.md", "UserAgents.md"]:
        src = INIT_TEMPLATE_DIR / filename
        dst = target_path / filename
        
        if dst.exists() and not force:
            logger.warning(f"Skipping {dst} (exists)")
            continue
            
        if src.exists():
            shutil.copy2(src, dst)
        else:
            logger.warning(f"Template {src} not found")
            atomic_write(dst, f"# {filename}\nGenerated by Copal.", overwrite=force)

def _install_packs(packs: List[str], copal_dir: Path, force: bool, dry_run: bool):
    if dry_run: return
    
    packs_dir = copal_dir / "packs"
    packs_dir.mkdir(exist_ok=True)
    
    skills_dir = copal_dir / "skills"
    skills_dir.mkdir(exist_ok=True)
    
    for pack_name in packs:
        src = PACKS_TEMPLATE_DIR / pack_name
        dst = packs_dir / pack_name
        
        if not src.exists():
            logger.warning(f"Pack template {pack_name} not found at {src}")
            continue

        if dst.exists():
            if force:
                shutil.rmtree(dst)
            else:
                logger.warning(f"Pack {pack_name} already installed")
                continue
        
        shutil.copytree(src, dst)
        
        # Also install pack's skill to .copal/skills/ for easy access
        pack_skill_dir = src / "skill"
        if pack_skill_dir.exists():
            target_skill_dir = skills_dir / f"copal-{pack_name}"
            if target_skill_dir.exists() and force:
                shutil.rmtree(target_skill_dir)
            if not target_skill_dir.exists():
                shutil.copytree(pack_skill_dir, target_skill_dir)
                logger.info(f"Installed skill 'copal-{pack_name}' to {target_skill_dir}")

def _init_memory(copal_dir: Path, force: bool, dry_run: bool):
    if dry_run: return
    
    mem_dir = copal_dir / "memory"
    mem_dir.mkdir(exist_ok=True)
    
    index_file = mem_dir / "index.json"
    if not index_file.exists() or force:
        atomic_write(index_file, '{\n  "memories": []\n}', overwrite=force)
    
    # Create subdirs for memory types if needed, or just flat structure
    # For now, index.json is enough for the simple JSON backend

def _install_docs(copal_dir: Path, force: bool, dry_run: bool):
    if dry_run: return
    
    docs_dir = copal_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    defaults = ["architecture.md", "conventions.md", "tech_stack.md"]
    for d in defaults:
        p = docs_dir / d
        if not p.exists():
            # In V2, we prefer to point to packs/references, but keeping local docs for project-specific overrides is fine.
            # We can symlink or just keep them as project-specific docs.
            p.write_text(f"# {d.replace('.md', '').replace('_', ' ').title()}\n\nAdd documentation here.\n")

