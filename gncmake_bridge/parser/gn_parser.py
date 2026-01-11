import re
from pathlib import Path
from typing import Any

from gncmake_bridge.ir import Target, TargetType


def strip_string(s: str) -> str:
    s = s.strip()
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    return s


def parse_list(value: str) -> list[str]:
    value = value.strip()
    if not value.startswith("[") or not value.endswith("]"):
        return []
    content = value[1:-1].strip()
    if not content:
        return []
    items = []
    current = ""
    in_string = False
    quote_char = None
    depth = 0

    for char in content:
        if not in_string:
            if char in ('"', "'"):
                in_string = True
                quote_char = char
                current += char
            elif char == "[":
                depth += 1
                current += char
            elif char == "]":
                depth -= 1
                current += char
            elif char == "," and depth == 0:
                if current.strip():
                    items.append(current.strip())
                current = ""
            else:
                current += char
        else:
            current += char
            if char == quote_char and (len(current) < 2 or current[-2] != "\\"):
                in_string = False
                quote_char = None

    if current.strip():
        items.append(current.strip())

    return [strip_string(item) for item in items if strip_string(item)]


def parse_gn_file(content: str) -> list[Target]:
    targets: list[Target] = []
    content = content.strip()
    lines = content.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        target_match = re.match(
            r'^(executable|static_library|shared_library|source_set|group|action|generated_file)\s*\(\s*["\']?(\w+)["\']?\s*\)',
            line,
        )
        if target_match:
            target_type_str = target_match.group(1)
            target_name = target_match.group(2)

            type_map = {
                "executable": TargetType.EXECUTABLE,
                "static_library": TargetType.STATIC_LIBRARY,
                "shared_library": TargetType.SHARED_LIBRARY,
                "source_set": TargetType.SOURCE_SET,
                "group": TargetType.GROUP,
                "action": TargetType.ACTION,
                "generated_file": TargetType.GENERATE_FILE,
            }
            target_type = type_map.get(target_type_str, TargetType.UNKNOWN)

            properties: dict[str, Any] = {}

            current_line = line
            brace_depth = current_line.count("{") - current_line.count("}")

            if brace_depth == 0:
                i += 1
                if i < len(lines):
                    next_line = lines[i].strip()
                    if next_line == "{":
                        brace_depth = 1
                        i += 1
            else:
                i += 1

            while i < len(lines) and brace_depth > 0:
                current_line = lines[i].rstrip()
                current_line_stripped = current_line.strip()

                brace_change = current_line_stripped.count("{") - current_line_stripped.count("}")
                brace_depth += brace_change

                if current_line_stripped and not current_line_stripped.startswith("//"):
                    prop_match = re.match(r"^(\w+)\s*=\s*(.+)$", current_line_stripped)
                    if prop_match:
                        prop_name = prop_match.group(1)
                        prop_value = prop_match.group(2).strip()

                        if prop_name in (
                            "sources",
                            "headers",
                            "deps",
                            "public_deps",
                            "private_deps",
                            "data_deps",
                            "cflags",
                            "cflags_cc",
                            "ldflags",
                            "include_dirs",
                            "defines",
                            "visibility",
                            "configs",
                        ):
                            properties[prop_name] = parse_list(prop_value)
                        elif prop_name == "output_name":
                            properties[prop_name] = strip_string(prop_value)
                        elif prop_name in ("testonly", "complete_static_lib"):
                            properties[prop_name] = prop_value == "true"

                i += 1
                if brace_depth == 0:
                    break

            target = Target(
                name=target_name,
                type=target_type,
                sources=properties.get("sources", []),
                headers=properties.get("headers", []),
                deps=properties.get("deps", []),
                public_deps=properties.get("public_deps", []),
                private_deps=properties.get("private_deps", []),
                data_deps=properties.get("data_deps", []),
                compile_flags=properties.get("cflags", []),
                link_flags=properties.get("ldflags", []),
                include_dirs=properties.get("include_dirs", []),
                defines=properties.get("defines", []),
                visibility=properties.get("visibility", []),
                output_name=properties.get("output_name"),
                configs=properties.get("configs", []),
            )
            targets.append(target)
        else:
            i += 1

    return targets


class GNParser:
    def __init__(self) -> None:
        pass

    def parse(self, content: str) -> list[Target]:
        return parse_gn_file(content)

    def parse_file(self, path: Path) -> list[Target]:
        content = path.read_text()
        return self.parse(content)
