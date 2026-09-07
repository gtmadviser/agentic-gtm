"""Package canonical skill resources without local sync copies or Python caches."""

from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        if self.target_name != "wheel":
            return
        source = Path(self.root) / "skills"
        for path in sorted(source.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts:
                continue
            if " 2." in path.name or path.suffix == ".pyc":
                continue
            destination = "agentic_gtm/resources/skills/" + path.relative_to(source).as_posix()
            build_data["force_include"][str(path)] = destination
