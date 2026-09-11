"""Package canonical skill resources without local sync copies or Python caches."""

from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        if self.target_name != "wheel":
            return
        if version == "editable":
            # An editable install exposes the package via a .pth pointing at src/.
            # force_include would additionally materialise a real
            # site-packages/agentic_gtm/resources/ tree with no __init__.py, which is
            # picked up as a namespace portion for "agentic_gtm" and shadows the source
            # package -- importing agentic_gtm then succeeds while agentic_gtm.workflows
            # raises ModuleNotFoundError. Editable installs read skills from the repo.
            return
        source = Path(self.root) / "skills"
        for path in sorted(source.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if " 2." in path.name or path.suffix == ".pyc":
                continue
            destination = "agentic_gtm/resources/skills/" + path.relative_to(source).as_posix()
            build_data["force_include"][str(path)] = destination
