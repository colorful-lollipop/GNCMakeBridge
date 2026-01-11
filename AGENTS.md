# AGENTS.md - GNCMakeBridge Development Guide

This document provides guidelines for agentic coding agents working on the GN ↔ CMake bidirectional conversion tool.

## Project Overview

GNCMakeBridge is a tool to convert between GN (Generate Ninja) and CMake build systems. The architecture uses an Intermediate Representation (IR) as the central data model:

```
GN Parser → AST → IR → CMake Generator → CMake
CMake Parser → AST → IR → GN Generator → GN
```

Key data structures: `Target` (name, type, sources, deps, flags, visibility, metadata), `Toolchain` (compiler, linker, sysroot, triple).

---

## Build Commands

```bash
# Python implementation (recommended for MVP)
pip install -e .
python -m gncmake_bridge --help

# Run all tests
python -m pytest tests/ -v

# Run single test file
python -m pytest tests/test_parser.py -v

# Run single test case
python -m pytest tests/test_parser.py::test_gn_executable -v

# Generate coverage report
python -m pytest tests/ --cov=gncmake_bridge --cov-report=html

# Linting
python -m ruff check gncmake_bridge/ tests/
python -m black gncmake_bridge/ tests/
python -m mypy gncmake_bridge/

# Type checking
python -m mypy gncmake_bridge/ --strict

# All quality checks
python -m ruff check gncmake_bridge/ tests/ && python -m black --check gncmake_bridge/ tests/ && python -m mypy gncmake_bridge/
```

For Rust implementation (performance-critical components):
```bash
cargo build --release
cargo test --release
cargo clippy
cargo fmt
```

---

## Code Style Guidelines

### General Principles

- Write self-documenting code with clear intent
- Prefer explicit over implicit
- Fail fast with descriptive error messages
- Design for extensibility (IR-first architecture)
- Maintain separation of concerns (parser → IR → generator)

### Python Style

- Follow PEP 8, enforced by `ruff` and `black`
- Use type hints for all function signatures and class attributes
- Module docstrings required for all public modules
- Line length: 100 characters (black default)
- Use `python -c` for CLI entry points with `argparse`

### Imports

```python
# Standard library first, then third-party, then local
import argparse
import sys
from pathlib import Path
from typing import Any

import pytest
from rich import print

from gncmake_bridge.ir import Target, IR
from gncmake_bridge.parser import GNParser
```

### Naming Conventions

- `snake_case` for functions, variables, modules
- `PascalCase` for classes and types
- `SCREAMING_SNAKE_CASE` for constants
- Prefix private methods with underscore: `_internal_method()`
- Prefix internal module names with underscore: `_internal_parser.py`

### Type Hints

```python
from typing import Protocol, TypeAlias, TypedDict

class GNTarget(TypedDict):
    name: str
    type: str
    sources: list[str]
    deps: list[str]

TargetDict: TypeAlias = dict[str, Any]

def parse_target(content: str, name: str) -> GNTarget:
    ...
```

### Error Handling

- Use custom exception hierarchy:
  - `GNCMakeBridgeError` (base)
  - `ParseError` (syntax errors)
  - `ConversionError` (semantic errors)
  - `GeneratorError` (output generation errors)

```python
class ParseError(GNCMakeBridgeError):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(f"Parse error at line {line}, col {column}: {message}")
        self.line = line
        self.column = column

def parse_gn_file(path: Path) -> IR:
    if not path.exists():
        raise ParseError(f"File not found: {path}", 0, 0)
```

### IR Design

The Intermediate Representation is the core data model:

```python
@dataclass
class Target:
    name: str
    type: TargetType  # enum: EXECUTABLE, STATIC_LIB, SHARED_LIB, etc.
    sources: list[str] = field(default_factory=list)
    headers: list[str] = field(default_factory=list)
    deps: list[str] = field(default_factory=list)
    public_deps: list[str] = field(default_factory=list)
    data_deps: list[str] = field(default_factory=list)
    compile_flags: list[str] = field(default_factory=list)
    link_flags: list[str] = field(default_factory=list)
    visibility: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def is_valid(self) -> bool:
        return bool(self.name and self.type)
```

### File Organization

```
gncmake_bridge/
├── __init__.py          # Public API exports
├── __main__.py          # CLI entry point
├── cli.py               # Argument parsing
├── ir/                  # Intermediate representation
│   ├── __init__.py
│   ├── target.py
│   └── toolchain.py
├── parser/              # GN and CMake parsers
│   ├── __init__.py
│   ├── gn_parser.py
│   └── cmake_parser.py
├── generator/           # Code generators
│   ├── __init__.py
│   ├── gn_generator.py
│   └── cmake_generator.py
└── converter/           # Conversion logic
    ├── __init__.py
    └── converter.py
```

### Testing

- Use `pytest` with fixtures for common setup
- Place tests in `tests/` mirroring source structure
- Test file naming: `test_<module>.py`
- Test class naming: `Test<ClassName>`
- Use parametrize for multiple test cases:

```python
@pytest.mark.parametrize("gn_input,expected", [
    ('executable("foo")', ...),
    ('static_library("bar")', ...),
])
def test_parse_target(gn_input: str, expected: dict):
    ...
```

### Documentation

- Public functions require docstrings with Args and Returns sections
- Complex algorithms include explanation comments
- Update README.md for user-facing changes
- Document IR schema changes in docs/ir_spec.md

---

## Development Workflow

1. Create feature branch from `main`
2. Implement IR changes first, then parser, then generator
3. Add tests before implementing conversion logic
4. Run full test suite and linting before committing
5. Ensure roundtrip tests pass (GN → IR → GN produces identical output)
