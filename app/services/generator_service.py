from pathlib import Path
import shutil


BASE_DIR = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = BASE_DIR / "templates" / "projects"


SUPPORTED_TEMPLATES = {
    "flask",
    "fastapi",
    "node",
}


def generate_project(template_type, destination):
    if template_type not in SUPPORTED_TEMPLATES:
        raise ValueError(
            f"Unsupported template type: {template_type}"
        )

    source = TEMPLATES_DIR / template_type
    destination = Path(destination)

    if not source.exists():
        raise FileNotFoundError(
            f"Template not found: {template_type}"
        )

    destination.mkdir(parents=True, exist_ok=True)

    for item in source.iterdir():
        target = destination / item.name

        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)