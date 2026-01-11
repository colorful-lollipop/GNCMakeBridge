from typing import Any

from gncmake_bridge.ir import Target, TargetType


class GNGenerator:
    def __init__(self, indent: str = "  ") -> None:
        self._indent = indent

    def generate(self, target: Target) -> str:
        lines = [self._generate_target(target)]
        return "\n".join(lines)

    def _generate_target(self, target: Target) -> str:
        type_str = self._type_to_string(target.type)
        lines = [f'{type_str}("{target.name}") {{']

        if target.sources:
            lines.append(f"{self._indent}sources = [")
            for source in target.sources:
                lines.append(f'{self._indent}  "{source}",')
            lines.append(f"{self._indent}]")

        if target.headers:
            lines.append(f"{self._indent}headers = [")
            for header in target.headers:
                lines.append(f'{self._indent}  "{header}",')
            lines.append(f"{self._indent}]")

        if target.deps:
            lines.append(f"{self._indent}deps = [")
            for dep in target.deps:
                lines.append(f'{self._indent}  "{dep}",')
            lines.append(f"{self._indent}]")

        if target.public_deps:
            lines.append(f"{self._indent}public_deps = [")
            for dep in target.public_deps:
                lines.append(f'{self._indent}  "{dep}",')
            lines.append(f"{self._indent}]")

        if target.private_deps:
            lines.append(f"{self._indent}private_deps = [")
            for dep in target.private_deps:
                lines.append(f'{self._indent}  "{dep}",')
            lines.append(f"{self._indent}]")

        if target.data_deps:
            lines.append(f"{self._indent}data_deps = [")
            for dep in target.data_deps:
                lines.append(f'{self._indent}  "{dep}",')
            lines.append(f"{self._indent}]")

        if target.compile_flags:
            lines.append(f"{self._indent}cflags = [")
            for flag in target.compile_flags:
                lines.append(f'{self._indent}  "{flag}",')
            lines.append(f"{self._indent}]")

        if target.link_flags:
            lines.append(f"{self._indent}ldflags = [")
            for flag in target.link_flags:
                lines.append(f'{self._indent}  "{flag}",')
            lines.append(f"{self._indent}]")

        if target.include_dirs:
            lines.append(f"{self._indent}include_dirs = [")
            for dir in target.include_dirs:
                lines.append(f'{self._indent}  "{dir}",')
            lines.append(f"{self._indent}]")

        if target.defines:
            lines.append(f"{self._indent}defines = [")
            for define in target.defines:
                lines.append(f'{self._indent}  "{define}",')
            lines.append(f"{self._indent}]")

        if target.visibility:
            lines.append(f"{self._indent}visibility = [")
            for v in target.visibility:
                lines.append(f'{self._indent}  "{v}",')
            lines.append(f"{self._indent}]")

        if target.output_name:
            lines.append(f'{self._indent}output_name = "{target.output_name}"')

        if target.configs:
            lines.append(f"{self._indent}configs = [")
            for config in target.configs:
                lines.append(f'{self._indent}  "{config}",')
            lines.append(f"{self._indent}]")

        lines.append("}")
        return "\n".join(lines)

    def _type_to_string(self, target_type: TargetType) -> str:
        type_map = {
            TargetType.EXECUTABLE: "executable",
            TargetType.STATIC_LIBRARY: "static_library",
            TargetType.SHARED_LIBRARY: "shared_library",
            TargetType.SOURCE_SET: "source_set",
            TargetType.GROUP: "group",
            TargetType.ACTION: "action",
            TargetType.GENERATE_FILE: "generated_file",
        }
        return type_map.get(target_type, "unknown")
