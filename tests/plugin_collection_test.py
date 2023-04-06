"""Testing plugin_collection."""
from filetransferautomation.plugin_collection import split_uppercase


def test_split_uppercase():
    """Testing split_uppercase."""
    assert split_uppercase("CoolPlugin") == "Cool_Plugin"
