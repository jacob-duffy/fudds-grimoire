"""Smoke tests for main entry point."""

from unittest.mock import MagicMock, patch

from grimoire.main import main


def test_main_runs():
    """main() should instantiate GrimoireApp and call run()."""
    with patch("grimoire.main.GrimoireApp") as MockApp:
        mock_instance = MagicMock()
        MockApp.return_value = mock_instance
        main()
        MockApp.assert_called_once()
        mock_instance.run.assert_called_once()
