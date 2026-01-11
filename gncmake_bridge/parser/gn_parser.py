import re
from pathlib import Path
from typing import Any

from lark import Lark, Transformer, v_args

from gncmake_bridge.ir import Target, TargetType


GRAMMAR = r"""
    start: file

    file: statement*

    statement: target_def
             | import_def
             | config_def
             | template_def
             | variable_assign
             | condition

    target_def: target_type "(" STRING ")" "{" target_body "}"

    target_type: "executable"
               | "static_library"
               | "shared_library"
               | "source_set"
               | "group"
               | "action"
               | "generated_file"

    target_body: target_property*

    target_property: "sources" "=" "[" list_items "]"
                   | "headers" "=" "[" list_items "]"
                   | "deps" "=" "[" list_items "]"
                   | "public_deps" "=" "[" list_items "]"
                   | "private_deps" "=" "[" list_items "]"
                   | "data_deps" "=" "[" list_items "]"
                   | "cflags" "=" "[" list_items "]"
                   | "cflags_cc" "=" "[" list_items "]"
                   | "ldflags" "=" "[" list_items "]"
                   | "include_dirs" "=" "[" list_items "]"
                   | "defines" "=" "[" list_items "]"
                   | "visibility" "=" "[" list_items "]"
                   | "output_name" "=" STRING
                   | "configs" "=" "[" list_items "]"
                   | "inputs" "=" "[" list_items "]"
                   | "outputs" "=" "[" list_items "]"
                   | "script" "=" STRING
                   | "response_file_name" "=" STRING
                   | "testonly" "=" bool_value
                   | "complete_static_lib" "=" bool_value
                   | condition

    list_items: (STRING | variable_ref)*
    variable_ref: "$" "(" NAME ")"

    import_def: "import" "(" STRING ")"
    config_def: "config" "(" NAME ")" "{" config_body "}"
    template_def: "template" "(" NAME ")" "{" template_body "}"
    variable_assign: NAME "=" value
    condition: "if" "(" expr ")" "{" statement* "}"

    config_body: config_property*
    config_property: "cflags" "=" "[" list_items "]"
                   | "include_dirs" "=" "[" list_items "]"
                   | "defines" "=" "[" list_items "]"

    template_body: statement*

    value: STRING
         | "[" list_items "]"
         | "true"
         | "false"

    bool_value: "true" | "false"

    expr: NAME ("|" NAME)*

    STRING: /"(?:[^"\\]|\\.)*"|\'(?:[^'\\]|\\.)*\'/
    NAME: /[a-zA-Z_][a-zA-Z0-9_]*/

    %ignore /\s+/
    %ignore "//" /[^\n]*/
"""


class GNTransformer(Transformer):
    def __init__(self) -> None:
        super().__init__()

    def start(self, items: Any) -> Any:
        return items

    def file(self, items: Any) -> Any:
        return [item for item in items if item is not None]

    def target_def(self, items: Any) -> Target | None:
        target_type_map = {
            "executable": TargetType.EXECUTABLE,
            "static_library": TargetType.STATIC_LIBRARY,
            "shared_library": TargetType.SHARED_LIBRARY,
            "source_set": TargetType.SOURCE_SET,
            "group": TargetType.GROUP,
            "action": TargetType.ACTION,
            "generated_file": TargetType.GENERATE_FILE,
        }
        target_type_str = str(items[0])
        target_type = target_type_map.get(target_type_str, TargetType.UNKNOWN)
        name = str(items[1]).strip('"\'')
        properties = items[2] if len(items) > 2 else {}

        return Target(
            name=name,
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

    def target_body(self, items: Any) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        for item in items:
            if isinstance(item, dict):
                properties.update(item)
        return properties

    def target_property(self, items: Any) -> tuple[str, Any]:
        key = str(items[0])
        value = items[1]
        if isinstance(value, list):
            value = [str(v).strip('"\'') for v in value]
        else:
            value = str(value).strip('"\'')
        return (key, value)

    def sources(self, items: Any) -> Any:
        return ("sources", items[1])

    def headers(self, items: Any) -> Any:
        return ("headers", items[1])

    def deps(self, items: Any) -> Any:
        return ("deps", items[1])

    def public_deps(self, items: Any) -> Any:
        return ("public_deps", items[1])

    def private_deps(self, items: Any) -> Any:
        return ("private_deps", items[1])

    def data_deps(self, items: Any) -> Any:
        return ("data_deps", items[1])

    def cflags(self, items: Any) -> Any:
        return ("cflags", items[1])

    def ldflags(self, items: Any) -> Any:
        return ("ldflags", items[1])

    def include_dirs(self, items: Any) -> Any:
        return ("include_dirs", items[1])

    def defines(self, items: Any) -> Any:
        return ("defines", items[1])

    def visibility(self, items: Any) -> Any:
        return ("visibility", items[1])

    def output_name(self, items: Any) -> Any:
        return ("output_name", str(items[1]).strip('"\''))

    def configs(self, items: Any) -> Any:
        return ("configs", items[1])

    def list_items(self, items: Any) -> list[str]:
        return [str(item).strip('"\'') for item in items]

    def STRING(self, token: Any) -> str:
        return str(token)[1:-1]

    def bool_value(self, items: Any) -> bool:
        return str(items[0]) == "true"


class GNParser:
    def __init__(self) -> None:
        self._parser = Lark(GRAMMAR, parser="lalr", transformer=GNTransformer())

    def parse(self, content: str) -> list[Target]:
        tree = self._parser.parse(content)
        return [node for node in tree if isinstance(node, Target)]

    def parse_file(self, path: Path) -> list[Target]:
        content = path.read_text()
        return self.parse(content)
