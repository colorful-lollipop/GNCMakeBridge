from dataclasses import dataclass, field


@dataclass
class GNTemplate:
    """GN template definition."""

    name: str
    variables: list[str] = field(default_factory=list)
    body: str = ""
    invocation_count: int = 0

    def is_valid(self) -> bool:
        return bool(self.name and self.variables)


@dataclass
class GNCondition:
    """GN condition block (if/else)."""

    condition: str
    then_body: str = ""
    else_body: str = ""
    elif_conditions: list[dict[str, str]] = field(default_factory=list)

    def is_valid(self) -> bool:
        return bool(self.condition)


@dataclass
class GNConfig:
    """GN config definition."""

    name: str
    cflags: list[str] = field(default_factory=list)
    cflags_cc: list[str] = field(default_factory=list)
    include_dirs: list[str] = field(default_factory=list)
    defines: list[str] = field(default_factory=list)
    visibility: list[str] = field(default_factory=list)


@dataclass
class GNImport:
    """GN import statement."""

    path: str
    is_public: bool = False
