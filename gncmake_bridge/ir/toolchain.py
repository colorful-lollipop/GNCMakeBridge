from dataclasses import dataclass, field
from typing import Any


@dataclass
class Toolchain:
    name: str = ""
    c_compiler: str = ""
    cxx_compiler: str = ""
    linker: str = ""
    ar: str = ""
    sysroot: str = ""
    target_triple: str = ""
    cmake_toolchain_file: str | None = None
    c_standard: str = "c11"
    cxx_standard: str = "c++17"
    flags: dict[str, str] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        return bool(self.name and (self.c_compiler or self.cmake_toolchain_file))
