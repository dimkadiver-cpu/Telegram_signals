from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

_DEFAULT_TEMPLATES_DIR = Path(__file__).parent / "default"


class TemplateEngine:
    """Jinja2 environment with support for default and custom (string) templates."""

    def __init__(self, templates_dir: Path = _DEFAULT_TEMPLATES_DIR) -> None:
        self._env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            autoescape=select_autoescape(disabled_extensions=("j2",)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def render_file(self, template_name: str, context: dict) -> str:
        """Render a template from file (e.g. 'open.j2')."""
        tmpl = self._env.get_template(template_name)
        return tmpl.render(**context)

    def render_string(self, template_str: str, context: dict) -> str:
        """Render an arbitrary Jinja2 string (custom trader template)."""
        tmpl = self._env.from_string(template_str)
        return tmpl.render(**context)
