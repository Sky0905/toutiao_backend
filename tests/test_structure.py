from pathlib import Path


def test_expected_layers_exist():
    root = Path(__file__).parents[1] / "app"
    for directory in ("crud", "models", "routers", "schemas", "utils"):
        assert (root / directory).is_dir()


def test_main_module_exists():
    assert (Path(__file__).parents[1] / "app" / "main.py").is_file()

