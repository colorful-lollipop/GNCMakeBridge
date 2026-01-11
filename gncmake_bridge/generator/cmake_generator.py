from typing import Any

from gncmake_bridge.ir import Target, TargetType


class CMakeGenerator:
    def __init__(self, indent: str = "  ") -> None:
        self._indent = indent

    def generate(self, target: Target) -> str:
        lines = [self._generate_target(target)]
        return "\n".join(lines)

    def _generate_target(self, target: Target) -> str:
        lines = []

        if target.type == TargetType.EXECUTABLE:
            lines.append(f"add_executable({target.name}")
            for source in target.sources:
                lines.append(f"  {source}")
            lines.append(")")
        elif target.type == TargetType.STATIC_LIBRARY:
            lines.append(f"add_library({target.name} STATIC")
            for source in target.sources:
                lines.append(f"  {source}")
            lines.append(")")
        elif target.type == TargetType.SHARED_LIBRARY:
            lines.append(f"add_library({target.name} SHARED")
            for source in target.sources:
                lines.append(f"  {source}")
            lines.append(")")
        elif target.type == TargetType.SOURCE_SET:
            lines.append(f"add_library({target.name} OBJECT")
            for source in target.sources:
                lines.append(f"  {source}")
            lines.append(")")
        elif target.type == TargetType.GROUP:
            lines.append(f"add_library({target.name} INTERFACE)")
        elif target.type == TargetType.ACTION:
            lines.append(f"add_custom_target({target.name} ALL)")
        else:
            lines.append(f"# Unknown target type: {target.type}")

        if target.include_dirs:
            visibility = self._get_visibility(target)
            for dir in target.include_dirs:
                lines.append(f"target_include_directories({target.name} {visibility} {dir})")

        if target.defines:
            visibility = self._get_visibility(target)
            for define in target.defines:
                lines.append(f"target_compile_definitions({target.name} {visibility} {define})")

        if target.compile_flags:
            visibility = self._get_visibility(target)
            flags_str = " ".join(target.compile_flags)
            lines.append(f"target_compile_options({target.name} {visibility} {flags_str})")

        if target.public_deps or target.private_deps or target.deps:
            self._generate_link_libraries(lines, target)

        if target.output_name:
            lines.append(f'set_target_properties({target.name} PROPERTIES OUTPUT_NAME "{target.output_name}")')

        return "\n".join(lines)

    def _get_visibility(self, target: Target) -> str:
        if target.public_deps:
            return "PUBLIC"
        elif target.private_deps:
            return "PRIVATE"
        return "PRIVATE"

    def _generate_link_libraries(self, lines: list[str], target: Target) -> None:
        all_deps = []
        if target.public_deps:
            all_deps.extend([(d, "PUBLIC") for d in target.public_deps])
        if target.private_deps:
            all_deps.extend([(d, "PRIVATE") for d in target.private_deps])
        if target.deps:
            all_deps.extend([(d, "PRIVATE") for d in target.deps])

        if all_deps:
            lines.append(f"target_link_libraries({target.name}")
            for dep, vis in all_deps:
                lines.append(f"  {dep}")
            lines.append(")")
