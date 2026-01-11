# GNCMakeBridge

Bidirectional converter between GN (Generate Ninja) and CMake build systems.

## Overview

GNCMakeBridge converts build definitions between GN and CMake formats, enabling:
- Migration from GN to CMake for IDE integration
- Migration from CMake to GN for Chromium ecosystem
- Mixed build environments with both systems

## Installation

```bash
pip install -e .
```

## Usage

```bash
# Convert GN to CMake
gncmake-bridge convert --mode gn-to-cmake --input /path/to/BUILD.gn --output /path/to/CMakeLists.txt

# Convert CMake to GN
gncmake-bridge convert --mode cmake-to-gn --input /path/to/CMakeLists.txt --output /path/to/BUILD.gn

# Show help
gncmake-bridge --help
```

## Architecture

```
GN Parser → AST → IR → CMake Generator → CMake
CMake Parser → AST → IR → GN Generator → GN
```

The Intermediate Representation (IR) is the core data model containing:
- `Target`: Build target with sources, deps, flags, visibility
- `Toolchain`: Compiler, linker, sysroot, and target triple

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
ruff check gncmake_bridge/ tests/
black gncmake_bridge/ tests/
mypy gncmake_bridge/
```

## License

MIT
