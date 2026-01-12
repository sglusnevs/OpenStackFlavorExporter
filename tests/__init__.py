import json
from unittest.mock import MagicMock
from pathlib import Path

def mock_openstack_connection(mock):
    mock_osclient = MagicMock()
    with open(Path(__file__).parent / "list_aggregates.json", encoding='utf-8') as file_handler:
        mock_osclient.list_aggregates.return_value = json.load(file_handler)
        file_handler.close()

    with open(Path(__file__).parent / "list_servers.json", encoding='utf-8') as file_handler:
        mock_osclient.list_servers.return_value = json.load(file_handler)
        file_handler.close()

    with open(Path(__file__).parent / "list_hypervisors.json", encoding='utf-8') as file_handler:
        mock_osclient.list_hypervisors.return_value = json.load(file_handler)
        file_handler.close()

    with open(Path(__file__).parent / "list_flavors.json", encoding='utf-8') as file_handler:
        mock_osclient.list_flavors.return_value = json.load(file_handler)
        file_handler.close()

    mock.return_value = mock_osclient
