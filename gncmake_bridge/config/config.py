"""Configuration file support for GNCMakeBridge."""
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from gncmake_bridge.exceptions import ConfigurationError

if sys.version_info >= (3, 11):
    pass
else:
    pass


@dataclass
class ProjectConfig:
    """Project-level configuration."""

    name: str = ""
    gn_root: str = "."
    output_dir: str = "cmake_output"


@dataclass
class ConversionConfig:
    """Conversion-related configuration."""

    mode: str = "gn_to_cmake"
    preserve_structure: bool = True
    human_readable: bool = True


@dataclass
class TargetsConfig:
    """Target filtering configuration."""

    include: list[str] = field(default_factory=list)
    exclude: list[str] = field(default_factory=list)


@dataclass
class CMakeConfig:
    """CMake-specific configuration."""

    minimum_version: str = "3.20"
    generator: str = "Ninja"
    use_ccache: bool = False
    c_standard: str = "11"
    cxx_standard: str = "17"
    options: dict[str, str] = field(default_factory=dict)


@dataclass
class ExternalMappingConfig:
    """External dependency mapping configuration."""

    mapping: dict[str, str] = field(default_factory=dict)


@dataclass
class GNCMakeConfig:
    """Complete configuration for GNCMakeBridge."""

    project: ProjectConfig = field(default_factory=ProjectConfig)
    conversion: ConversionConfig = field(default_factory=ConversionConfig)
    targets: TargetsConfig = field(default_factory=TargetsConfig)
    cmake: CMakeConfig = field(default_factory=CMakeConfig)
    external_mapping: ExternalMappingConfig = field(default_factory=ExternalMappingConfig)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GNCMakeConfig":
        """Create config from dictionary."""
        config = cls()

        if "project" in data:
            config.project = ProjectConfig(**data["project"])

        if "conversion" in data:
            config.conversion = ConversionConfig(**data["conversion"])

        if "targets" in data:
            config.targets = TargetsConfig(**data["targets"])

        if "cmake" in data:
            cmake_data = data["cmake"].copy()
            if "options" in cmake_data:
                cmake_data["options"] = cmake_data["options"]
            config.cmake = CMakeConfig(**cmake_data)

        if "dependencies" in data and "external_mapping" in data["dependencies"]:
            config.external_mapping = ExternalMappingConfig(
                mapping=data["dependencies"]["external_mapping"]
            )

        return config

    def to_dict(self) -> dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "project": {
                "name": self.project.name,
                "gn_root": self.project.gn_root,
                "output_dir": self.project.output_dir,
            },
            "conversion": {
                "mode": self.conversion.mode,
                "preserve_structure": self.conversion.preserve_structure,
                "human_readable": self.conversion.human_readable,
            },
            "targets": {
                "include": self.targets.include,
                "exclude": self.targets.exclude,
            },
            "cmake": {
                "minimum_version": self.cmake.minimum_version,
                "generator": self.cmake.generator,
                "use_ccache": self.cmake.use_ccache,
                "c_standard": self.cmake.c_standard,
                "cxx_standard": self.cmake.cxx_standard,
                "options": self.cmake.options,
            },
            "dependencies": {
                "external_mapping": self.external_mapping.mapping,
            },
        }


def load_config(path: Path | str | None = None) -> GNCMakeConfig:
    """Load configuration from file.

    Args:
        path: Path to configuration file. If None, looks for gncmake.toml in current directory.

    Returns:
        GNCMakeConfig instance.

    Raises:
        ConfigurationError: If config file is invalid or not found.
    """
    import tomllib

    if path is None:
        possible_paths = [
            Path("gncmake.toml"),
            Path.cwd() / "gncmake.toml",
            Path.home() / ".gncmake.toml",
        ]
        for p in possible_paths:
            if p.exists():
                path = p
                break
        else:
            return GNCMakeConfig()

    if isinstance(path, str):
        path = Path(path)

    if not path.exists():
        raise ConfigurationError(f"Configuration file not found: {path}")

    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
        return GNCMakeConfig.from_dict(data)
    except tomllib.TOMLDecodeError as e:
        raise ConfigurationError(f"Invalid TOML in {path}: {e}") from e
    except OSError as e:
        raise ConfigurationError(f"Failed to read {path}: {e}") from e
