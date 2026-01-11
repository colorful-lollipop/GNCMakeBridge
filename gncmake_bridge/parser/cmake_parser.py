import re
from pathlib import Path
from typing import Any

from gncmake_bridge.ir import Target, TargetType


def parse_cmake_file(content: str) -> list[Target]:
    targets: list[Target] = []
    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("add_executable("):
            target = parse_executable(line, lines, i)
            if target:
                targets.append(target)
                i = find_closing_brace(lines, i) + 1
                continue

        elif line.startswith("add_library("):
            target = parse_library(line, lines, i)
            if target:
                targets.append(target)
                i = find_closing_brace(lines, i) + 1
                continue

        elif line.startswith("add_custom_target("):
            target = parse_custom_target(line, lines, i)
            if target:
                targets.append(target)
                i = find_closing_brace(lines, i) + 1
                continue

        i += 1

    return targets


def parse_executable(first_line: str, lines: list[str], start_idx: int) -> Target | None:
    match = re.match(r"add_executable\s*\(\s*(\w+)\s+(.+)\)", first_line)
    if not match:
        return None

    name = match.group(1)
    sources = match.group(2).split()

    target = Target(name=name, type=TargetType.EXECUTABLE, sources=sources)

    i = start_idx + 1
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith(")"):
            break

        if line.startswith("target_link_libraries("):
            parse_link_libraries(line, target)
        elif line.startswith("target_include_directories("):
            parse_include_directories(line, target)
        elif line.startswith("target_compile_definitions("):
            parse_compile_definitions(line, target)
        elif line.startswith("target_compile_options("):
            parse_compile_options(line, target)
        elif line.startswith("set_target_properties("):
            parse_target_properties(line, target)

        i += 1

    return target


def parse_library(first_line: str, lines: list[str], start_idx: int) -> Target | None:
    lib_type = "STATIC"
    match = re.match(r"add_library\s*\(\s*(\w+)\s+(\w+)?\s*(.*)\)", first_line)
    if not match:
        return None

    name = match.group(1)
    type_str = match.group(2)
    rest = match.group(3) if match.group(3) else ""

    if type_str in ("STATIC", "SHARED", "OBJECT", "INTERFACE"):
        lib_type = type_str
        sources = rest.split() if rest else []
    else:
        sources = (type_str + " " + rest).split()

    type_map = {
        "STATIC": TargetType.STATIC_LIBRARY,
        "SHARED": TargetType.SHARED_LIBRARY,
        "OBJECT": TargetType.SOURCE_SET,
        "INTERFACE": TargetType.GROUP,
    }

    target = Target(name=name, type=type_map.get(lib_type, TargetType.UNKNOWN), sources=sources)

    i = start_idx + 1
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith(")"):
            break

        if line.startswith("target_link_libraries("):
            parse_link_libraries(line, target)
        elif line.startswith("target_include_directories("):
            parse_include_directories(line, target)
        elif line.startswith("target_compile_definitions("):
            parse_compile_definitions(line, target)
        elif line.startswith("target_compile_options("):
            parse_compile_options(line, target)
        elif line.startswith("set_target_properties("):
            parse_target_properties(line, target)

        i += 1

    return target


def parse_custom_target(first_line: str, lines: list[str], start_idx: int) -> Target | None:
    match = re.match(r"add_custom_target\s*\(\s*(\w+)\s+(.*)", first_line)
    if not match:
        return None

    name = match.group(1)
    target = Target(name=name, type=TargetType.ACTION)

    return target


def parse_link_libraries(line: str, target: Target) -> None:
    match = re.match(r"target_link_libraries\s*\(\s*\w+\s+(PRIVATE|PUBLIC|INTERFACE)?\s*(.+)\)", line)
    if match:
        visibility = match.group(1) or "PRIVATE"
        libs = match.group(2).split()
        for lib in libs:
            lib = lib.strip()
            if lib.startswith("$<") or lib in ("PUBLIC", "PRIVATE", "INTERFACE"):
                continue
            if visibility == "PRIVATE":
                target.private_deps.append(lib)
            elif visibility == "PUBLIC":
                target.public_deps.append(lib)
            else:
                target.deps.append(lib)


def parse_include_directories(line: str, target: Target) -> None:
    match = re.match(r"target_include_directories\s*\(\s*\w+\s+(SYSTEM\s+)?(PRIVATE|PUBLIC|INTERFACE)?\s*(.+)\)", line)
    if match:
        dirs = match.group(3).split()
        target.include_dirs.extend([d.strip() for d in dirs if not d.startswith("$<")])


def parse_compile_definitions(line: str, target: Target) -> None:
    match = re.match(r"target_compile_definitions\s*\(\s*\w+\s+(PRIVATE|PUBLIC|INTERFACE)?\s*(.+)\)", line)
    if match:
        defs = match.group(2).split()
        target.defines.extend([d.replace("-D", "").strip() for d in defs if not d.startswith("$<")])


def parse_compile_options(line: str, target: Target) -> None:
    match = re.match(r"target_compile_options\s*\(\s*\w+\s+(PRIVATE|PUBLIC|INTERFACE)?\s*(.+)\)", line)
    if match:
        opts = match.group(2).split()
        target.compile_flags.extend([o.strip() for o in opts if not o.startswith("$<")])


def parse_target_properties(line: str, target: Target) -> None:
    match = re.match(r"set_target_properties\s*\(\s*\w+\s+PROPERTIES\s+(.+)\)", line)
    if match:
        props_str = match.group(1)
        output_match = re.search(r'OUTPUT_NAME\s+"([^"]+)"', props_str)
        if output_match:
            target.output_name = output_match.group(1)


def find_closing_brace(lines: list[str], start_idx: int) -> int:
    depth = 0
    for i in range(start_idx, len(lines)):
        line = lines[i]
        depth += line.count("{") - line.count("}")
        if depth == 0:
            return i
    return len(lines) - 1


class CMakeParser:
    def __init__(self) -> None:
        pass

    def parse(self, content: str) -> list[Target]:
        return parse_cmake_file(content)

    def parse_file(self, path: Path) -> list[Target]:
        content = path.read_text()
        return self.parse(content)
