from __future__ import annotations

import json
import logging
import subprocess
from pathlib import Path

import jsonschema
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from copal_cli.config.manifest import Manifest
from copal_cli.config.pack import Pack

logger = logging.getLogger(__name__)
console = Console()

def validate_command(target: str = ".", check_artifacts: bool = False) -> int:
    """
    Validate Copal configuration and optionally artifacts.
    
    Args:
        target: Target repository path.
        check_artifacts: Whether to validate artifacts against schemas.
        
    Returns:
        0 for success, 2 for config error, 3 for artifact error.
    """
    target_path = Path(target).resolve()
    manifest_path = target_path / ".copal" / "manifest.yaml"
    
    # 1. Validate Manifest
    if not manifest_path.exists():
        console.print(f"[red]✗ Manifest not found at {manifest_path}[/red]")
        return 2

    try:
        manifest = Manifest.load(manifest_path)
        console.print("[green]✓ manifest.yaml is valid[/green]")
    except Exception as e:
        console.print(f"[red]✗ manifest.yaml invalid: {e}[/red]")
        return 2

    # 2. Validate Packs
    has_error = False
    valid_packs = []
    
    packs_list = manifest.packs
    
    for pack_ref in packs_list:
        name = "unknown"
        pack_path = None
        
        if isinstance(pack_ref, str):
            name = pack_ref
            pack_path = target_path / ".copal" / "packs" / pack_ref
        elif isinstance(pack_ref, dict):
            name = pack_ref.get("name", "unknown")
            path_str = pack_ref.get("path")
            if path_str:
                pack_path = target_path / path_str

        if not pack_path:
             console.print(f"[yellow]⚠ Could not resolve path for pack: {pack_ref}[/yellow]")
             continue
             
        try:
            pack = Pack.load(pack_path)
            console.print(f"[green]✓ Pack '{pack.name}' is valid[/green]")
            valid_packs.append(pack)
            
            # Strict validation of resources
            resource_types = [
                ("Workflow", pack.workflows, pack.get_workflow_path),
                ("Prompt", pack.prompts, pack.get_prompt_path),
                ("Script", pack.scripts, pack.get_script_path),
                ("Template", pack.templates, pack.get_template_path),
            ]
            
            for r_type, r_map, r_getter in resource_types:
                for r_name in r_map:
                    path = r_getter(r_name)
                    if not path or not path.exists():
                        console.print(f"[red]✗ {r_type} '{r_name}' declared but missing at {path}[/red]")
                        has_error = True

        except Exception as e:
            console.print(f"[red]✗ Pack '{name}' invalid at {pack_path}: {e}[/red]")
            has_error = True

    if has_error:
        return 2

    # 3. Artifact Validation
    if check_artifacts:
        console.print("\n[bold]Validating Artifacts...[/bold]")
        artifact_error = False
        artifacts_dir = target_path / manifest.artifacts.dir
        
        if not artifacts_dir.exists():
             console.print(f"[yellow]⚠ Artifacts directory not found: {artifacts_dir}[/yellow]")
             return 0

        # Collect schemas from all packs
        for pack in valid_packs:
            for schema_name, schema_rel_path in pack.schemas.items():
                schema_path = pack.get_schema_path(schema_name)
                
                if not schema_path or not schema_path.exists():
                    console.print(f"[yellow]⚠ Schema '{schema_name}' missing in pack '{pack.name}'[/yellow]")
                    continue
                
                # Assume artifact filename matches schema name (e.g. plan -> plan.json)
                # This is a convention for v0.1
                artifact_file = artifacts_dir / f"{schema_name}.json"
                
                if not artifact_file.exists():
                    # It's okay if artifact doesn't exist yet (workflow didn't reach that stage)
                    # But if we want strict validation of *existing* artifacts, we skip missing ones.
                    continue
                    
                try:
                    with open(schema_path, "r") as f:
                        schema = json.load(f)
                    
                    with open(artifact_file, "r") as f:
                        instance = json.load(f)
                        
                    jsonschema.validate(instance=instance, schema=schema)
                    console.print(f"[green]✓ Artifact '{artifact_file.name}' matches schema '{schema_name}'[/green]")
                    
                except json.JSONDecodeError as e:
                     console.print(f"[red]✗ Artifact '{artifact_file.name}' is invalid JSON: {e}[/red]")
                     artifact_error = True
                except jsonschema.ValidationError as e:
                     console.print(f"[red]✗ Artifact '{artifact_file.name}' schema validation failed: {e.message}[/red]")
                     artifact_error = True
                except Exception as e:
                     console.print(f"[red]✗ Error validating '{artifact_file.name}': {e}[/red]")
                     artifact_error = True
        
        if artifact_error:
            return 3

    return 0


def validate_pre_task(target: str = ".") -> int:
    """
    Perform pre-task checks:
    1. Git status (must be clean)
    2. Run test command (must pass)
    """
    target_path = Path(target).resolve()
    manifest_path = target_path / ".copal" / "manifest.yaml"
    
    console.print("[bold]Running Pre-Task Validation...[/bold]")
    
    # 0. Check Git Status
    try:
        # Check for uncommitted changes
        status = subprocess.check_output(
            ["git", "status", "--porcelain"], 
            cwd=target_path, 
            text=True
        ).strip()
        
        if status:
            console.print("[red]✗ Uncommitted changes found. Please commit or stash them before starting a new task.[/red]")
            console.print(status)
            return 1
        console.print("[green]✓ Git working directory is clean[/green]")
        
    except FileNotFoundError:
        console.print("[yellow]⚠ Not a git repository, skipping git check[/yellow]")
    except subprocess.CalledProcessError:
        console.print("[red]✗ Failed to check git status[/red]")
        return 1

    # 1. Load Manifest for Test Command
    if not manifest_path.exists():
        console.print(f"[red]✗ Manifest not found at {manifest_path}[/red]")
        return 2
        
    try:
        manifest = Manifest.load(manifest_path)
    except Exception as e:
        console.print(f"[red]✗ manifest.yaml invalid: {e}[/red]")
        return 2

    # 2. Run Test Command (uses manifest.verify.command)
    if manifest.verify and manifest.verify.command:
        cmd = manifest.verify.command
        console.print(f"[bold]Running verification: {cmd}...[/bold]")
        try:
            subprocess.check_call(cmd, shell=True, cwd=target_path)
            console.print("[green]✓ Verification command passed[/green]")
        except subprocess.CalledProcessError:
            console.print(f"[red]✗ Verification Failed: Command '{cmd}' returned non-zero exit status[/red]")
            return 1
    else:
        console.print("[yellow]⚠ No verify.command configured in manifest, skipping verification[/yellow]")

    console.print("\n[green bold]✓ Pre-task validation passed! Ready to start task.[/green bold]")
    return 0

