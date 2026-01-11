import re
from pathlib import Path

from gncmake_bridge.ir import Target, TargetType


def parse_cmake_file(content: str) -> list[Target]:
    targets: list[Target] = []
    lines = content.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("add_executable("):
            target = parse_executable(lines, i)
            if target:
                targets.append(target)
            i += 1
            continue

        elif line.startswith("add_library("):
            target = parse_library(lines, i)
            if target:
                targets.append(target)
            i += 1
            continue

        elif line.startswith("add_custom_target("):
            target = parse_custom_target(lines, i)
            if target:
                targets.append(target)
            i += 1
            continue

        i += 1

    return targets


def extract_paren_content(lines: list[str], start_idx: int, start_pos: int = 0) -> list[str]:
    depth = 0
    in_string = False
    quote_char = None
    content_lines: list[str] = []
    current_line = ""
    first_paren_found = True

    for idx in range(start_idx, len(lines)):
        line = lines[idx]
        line_start = start_pos if idx == start_idx else 0

        for i in range(line_start, len(line)):
            char = line[i]

            if not in_string:
                if char in ('"', "'"):
                    in_string = True
                    quote_char = char
                    current_line += char
                elif char == "(":
                    if first_paren_found:
                        depth += 1
                    else:
                        first_paren_found = True
                    current_line += char
                elif char == ")":
                    if first_paren_found:
                        if depth == 0:
                            if current_line.strip():
                                content_lines.append(current_line.strip())
                            return content_lines
                        depth -= 1
                    current_line += char
                else:
                    current_line += char
            else:
                current_line += char
                if char == quote_char and (i == 0 or line[i - 1] != "\\"):
                    in_string = False

        if current_line.strip():
            content_lines.append(current_line.strip())
        current_line = ""

    return content_lines


def parse_executable(lines: list[str], start_idx: int) -> Target | None:
    line = lines[start_idx].strip()
    paren_start = line.index("(")

    content_lines = extract_paren_content(lines, start_idx, paren_start + 1)

    if not content_lines:
        return None

    first_line = content_lines[0]
    name_match = re.match(r"(\w+)\s*(.*)", first_line)
    if not name_match:
        return None

    name = name_match.group(1)

    sources = []
    for source_line in content_lines[1:]:
        parts = source_line.split()
        sources.extend(parts)

    sources = [s for s in sources if s and s != "WIN32" and s != "MACOSX_BUNDLE"]

    target = Target(name=name, type=TargetType.EXECUTABLE, sources=sources)

    parse_target_commands(lines, start_idx + 1, target)

    return target


def parse_library(lines: list[str], start_idx: int) -> Target | None:
    line = lines[start_idx].strip()
    paren_start = line.index("(")

    content_lines = extract_paren_content(lines, start_idx, paren_start + 1)

    if not content_lines:
        return None

    first_line = content_lines[0]
    match = re.match(r"(\w+)\s*(STATIC|SHARED|OBJECT|INTERFACE)?\s*(.*)", first_line)
    if not match:
        return None

    name = match.group(1)
    type_str = match.group(2) or "STATIC"

    sources = []
    for source_line in content_lines[1:]:
        parts = source_line.split()
        sources.extend(parts)

    sources = [s for s in sources if s] if sources else []

    type_map = {
        "STATIC": TargetType.STATIC_LIBRARY,
        "SHARED": TargetType.SHARED_LIBRARY,
        "OBJECT": TargetType.SOURCE_SET,
        "INTERFACE": TargetType.GROUP,
    }

    target = Target(name=name, type=type_map.get(type_str, TargetType.UNKNOWN), sources=sources)

    parse_target_commands(lines, start_idx + 1, target)

    return target


def parse_custom_target(lines: list[str], start_idx: int) -> Target | None:
    line = lines[start_idx].strip()
    paren_start = line.index("(")

    content_lines = extract_paren_content(lines, start_idx, paren_start + 1)

    if not content_lines:
        return None

    first_line = content_lines[0]
    name_match = re.match(r"(\w+)\s*(.*)", first_line)
    if not name_match:
        return None

    name = name_match.group(1)
    target = Target(name=name, type=TargetType.ACTION)

    return target


def parse_target_commands(lines: list[str], start_idx: int, target: Target) -> None:
    for idx in range(start_idx, len(lines)):
        line = lines[idx].strip()

        if not line or line.startswith("#"):
            continue

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


def parse_link_libraries(line: str, target: Target) -> None:
    try:
        content = line[line.index("(") + 1 : line.rindex(")")]
    except ValueError:
        return
    parts = content.split()
    if not parts:
        return

    for i, token in enumerate(parts):
        if token in ("PRIVATE", "PUBLIC", "INTERFACE"):
            continue
        if token.startswith("$<"):
            continue
        if token:
            if i > 0:
                prev = parts[i - 1]
                if prev == "PUBLIC":
                    target.public_deps.append(token)
                elif prev == "PRIVATE":
                    target.private_deps.append(token)
                else:
                    target.deps.append(token)
            else:
                target.deps.append(token)


def parse_include_directories(line: str, target: Target) -> None:
    try:
        content = line[line.index("(") + 1 : line.rindex(")")]
    except ValueError:
        return
    parts = content.split()
    if len(parts) < 2:
        return

    for token in parts[1:]:
        if token in ("SYSTEM", "BEFORE", "PRIVATE", "PUBLIC", "INTERFACE"):
            continue
        if token.startswith("$<"):
            continue
        if token:
            target.include_dirs.append(token)


def parse_compile_definitions(line: str, target: Target) -> None:
    try:
        content = line[line.index("(") + 1 : line.rindex(")")]
    except ValueError:
        return
    parts = content.split()
    if len(parts) < 2:
        return

    for token in parts[1:]:
        if token in ("PRIVATE", "PUBLIC", "INTERFACE"):
            continue
        if token.startswith("$<"):
            continue
        if token.startswith("-D"):
            target.defines.append(token[2:])
        elif token:
            target.defines.append(token)


def parse_compile_options(line: str, target: Target) -> None:
    try:
        content = line[line.index("(") + 1 : line.rindex(")")]
    except ValueError:
        return
    parts = content.split()
    if len(parts) < 2:
        return

    for token in parts[1:]:
        if token in ("PRIVATE", "PUBLIC", "INTERFACE"):
            continue
        if token.startswith("$<"):
            continue
        if token:
            target.compile_flags.append(token)


def parse_target_properties(line: str, target: Target) -> None:
    try:
        content = line[line.index("(") + 1 : line.rindex(")")]
    except ValueError:
        return
    output_match = re.search(r'OUTPUT_NAME\s+"([^"]+)"', content)
    if output_match:
        target.output_name = output_match.group(1)


class CMakeParser:
    def __init__(self) -> None:
        pass

    def parse(self, content: str) -> list[Target]:
        return parse_cmake_file(content)

    def parse_file(self, path: Path) -> list[Target]:
        content = path.read_text()
        return self.parse(content)
