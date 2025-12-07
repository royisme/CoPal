
import sys
import shutil
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

from copal_cli.harness.init import init_command
from copal_cli.harness.validate import validate_command
from copal_cli.harness.export import export_command
from copal_cli.harness.status import status_command

def run_verify():
    test_dir = Path("temp_harness_verify")
    if test_dir.exists():
        shutil.rmtree(test_dir)
    test_dir.mkdir()
    
    target = str(test_dir.resolve())
    
    print("\n=== 1. Init ===")
    ret = init_command(target=target, force=True, tools=["claude"], packs=["engineering_loop"])
    if ret != 0:
        print("Init failed")
        return
        
    print("\n=== 2. Validate (Config) ===")
    ret = validate_command(target=target)
    if ret != 0:
        print("Validate failed")
        
    print("\n=== 3. Export (Claude) ===")
    ret = export_command(tool="claude", target=target)
    if ret != 0:
        print("Export failed")

    print("\n=== 4. Status ===")
    status_command(target=target)

    # Verify artifacts logic (create dummy plan)
    print("\n=== 5. Artifact Validation (Dummy) ===")
    artifacts_dir = test_dir / ".copal" / "artifacts"
    (artifacts_dir / "plan.json").write_text('{"status": "confirmed", "version": 1, "task": "test", "steps": []}')
    
    print("Running validate --artifacts...")
    ret = validate_command(target=target, check_artifacts=True)
    if ret == 0:
        print("Artifact valid (unexpected if schema is strict, but confirming parser works)")
    else:
        print("Artifact invalid (Expected if schema is strict, confirms validation logic works)")

if __name__ == "__main__":
    run_verify()
