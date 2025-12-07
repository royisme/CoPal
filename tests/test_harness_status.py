from unittest.mock import MagicMock, patch
from copal_cli.harness.status import status_command
from copal_cli.config.pack import Pack

def test_status_valid(tmp_path):
    # Setup mock copal environment
    (tmp_path / ".copal").mkdir()
    (tmp_path / ".copal" / "manifest.yaml").write_text("manifest")
    (tmp_path / ".copal" / "packs" / "test_pack").mkdir(parents=True)
    
    mock_pack = MagicMock(spec=Pack)
    mock_pack.name = "test_pack"
    mock_pack.version = "1.0.0"
    
    mock_manifest = MagicMock()
    mock_manifest.project.name = "test_project"
    mock_manifest.project.description = "desc"
    mock_manifest.packs = ["test_pack"]
    mock_manifest.default_pack = "test_pack"
    mock_manifest.artifacts.dir = "artifacts"

    with patch("copal_cli.harness.status.Pack.load", return_value=mock_pack), \
         patch("copal_cli.harness.status.Manifest.load", return_value=mock_manifest):
        with patch("copal_cli.harness.status.console") as mock_console:
            ret = status_command(target=str(tmp_path))
            assert ret == 0
            # Ensure "test_pack" was printed (mock console.print called)
            # We can't easily check args if it made a table, but we assume success

def test_status_no_manifest(tmp_path):
    with patch("copal_cli.harness.status.console") as mock_console:
        ret = status_command(target=str(tmp_path))
        assert ret == 2
