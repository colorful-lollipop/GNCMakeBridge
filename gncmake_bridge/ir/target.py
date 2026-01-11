from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TargetType(Enum):
    EXECUTABLE = "executable"
    STATIC_LIBRARY = "static_library"
    SHARED_LIBRARY = "shared_library"
    SOURCE_SET = "source_set"
    GROUP = "group"
    ACTION = "action"
    GENERATE_FILE = "generated_file"
    UNKNOWN = "unknown"


@dataclass
class Target:
    name: str
    type: TargetType
    sources: list[str] = field(default_factory=list)
    headers: list[str] = field(default_factory=list)
    deps: list[str] = field(default_factory=list)
    public_deps: list[str] = field(default_factory=list)
    private_deps: list[str] = field(default_factory=list)
    data_deps: list[str] = field(default_factory=list)
    compile_flags: list[str] = field(default_factory=list)
    link_flags: list[str] = field(default_factory=list)
    include_dirs: list[str] = field(default_factory=list)
    defines: list[str] = field(default_factory=list)
    visibility: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
    output_name: str | None = None
    configs: list[str] = field(default_factory=list)
    conditions: list[dict[str, Any]] = field(default_factory=list)

    def is_valid(self) -> bool:
        return bool(self.name and self.type != TargetType.UNKNOWN)

    def is_library(self) -> bool:
        return self.type in (
            TargetType.STATIC_LIBRARY,
            TargetType.SHARED_LIBRARY,
            TargetType.SOURCE_SET,
        )

    def is_binary(self) -> bool:
        return self.type == TargetType.EXECUTABLE
