"""Comprehensive test suite for GNCMakeBridge."""
import tempfile
from pathlib import Path

from gncmake_bridge import (
    CMakeGenerator,
    CMakeParser,
    ConversionMode,
    Converter,
    GNGenerator,
    GNParser,
    Target,
    TargetType,
)


class TestGNParserAdvanced:
    """Advanced tests for GN parser."""

    def setup_method(self) -> None:
        self.parser = GNParser()

    def test_parse_action_with_script(self) -> None:
        """Test parsing action with script."""
        gn_content = '''
action("generate_foo") {
  script = "//tools/generate_foo.py"
  inputs = ["input.txt"]
  outputs = ["foo.cc"]
  deps = [":bar"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert targets[0].type == TargetType.ACTION
        assert targets[0].script == "//tools/generate_foo.py"
        assert "input.txt" in targets[0].inputs
        assert "foo.cc" in targets[0].outputs
        assert ":bar" in targets[0].deps

    def test_parse_with_response_file_name(self) -> None:
        """Test parsing with response file name."""
        gn_content = '''
static_library("mylib") {
  sources = ["lib.cc"]
  response_file_name = "mylib.rsp"
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert targets[0].response_file_name == "mylib.rsp"

    def test_parse_with_testonly(self) -> None:
        """Test parsing with testonly flag."""
        gn_content = '''
executable("unittest") {
  sources = ["test.cc"]
  testonly = true
  deps = [":base"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert targets[0].testonly is True

    def test_parse_group(self) -> None:
        """Test parsing group target."""
        gn_content = '''
group("mygroup") {
  deps = [":lib1", ":lib2", ":lib3"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert targets[0].type == TargetType.GROUP
        assert len(targets[0].deps) == 3

    def test_parse_with_configs(self) -> None:
        """Test parsing with configs."""
        gn_content = '''
executable("myapp") {
  sources = ["main.cc"]
  configs = [":debug_config", ":release_config"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert len(targets[0].configs) == 2

    def test_parse_empty_list(self) -> None:
        """Test parsing empty list properties."""
        gn_content = '''
executable("empty_app") {
  sources = []
  deps = []
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert targets[0].sources == []
        assert targets[0].deps == []

    def test_parse_complex_flags(self) -> None:
        """Test parsing complex compiler/linker flags."""
        gn_content = '''
shared_library("myshared") {
  sources = ["shared.cc"]
  cflags = ["-O3", "-Wall", "-Wextra", "-std=c++17"]
  ldflags = ["-L/usr/local/lib", "-lfoo"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert "-O3" in targets[0].compile_flags
        assert "-std=c++17" in targets[0].compile_flags
        assert "-L/usr/local/lib" in targets[0].link_flags

    def test_parse_multiple_source_sets(self) -> None:
        """Test parsing multiple source_set targets."""
        gn_content = '''
source_set("core") {
  sources = ["core.cc", "utils.cc"]
  headers = ["core.h", "utils.h"]
}

source_set("ui") {
  sources = ["ui.cc"]
  deps = [":core"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 2
        assert all(t.type == TargetType.SOURCE_SET for t in targets)

    def test_parse_generated_file(self) -> None:
        """Test parsing generated_file target."""
        gn_content = '''
generated_file("proto_out") {
  sources = ["proto/message.proto"]
  outputs = ["message.cc", "message.h"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert targets[0].type == TargetType.GENERATE_FILE


class TestCMakeParserAdvanced:
    """Advanced tests for CMake parser."""

    def setup_method(self) -> None:
        self.parser = CMakeParser()

    def test_parse_library_with_object_type(self) -> None:
        """Test parsing OBJECT library."""
        cmake_content = '''
add_library(core OBJECT
  core.cc
  utils.cc
)

target_include_directories(core PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
'''
        targets = self.parser.parse(cmake_content)
        assert len(targets) == 1
        assert targets[0].type == TargetType.SOURCE_SET

    def test_parse_interface_library(self) -> None:
        """Test parsing INTERFACE library."""
        cmake_content = '''
add_library(myinterface INTERFACE)
target_include_directories(myinterface INTERFACE ${CMAKE_CURRENT_SOURCE_DIR}/include)
'''
        targets = self.parser.parse(cmake_content)
        assert len(targets) == 1
        assert targets[0].type == TargetType.GROUP

    def test_parse_with_compile_options(self) -> None:
        """Test parsing target_compile_options."""
        cmake_content = '''
add_executable(myapp main.cc)

target_compile_options(myapp PRIVATE -Wall -O2 -g)
'''
        targets = self.parser.parse(cmake_content)
        assert len(targets) == 1
        assert "-Wall" in targets[0].compile_flags
        assert "-O2" in targets[0].compile_flags

    def test_parse_multiple_link_libraries(self) -> None:
        """Test parsing multiple linked libraries."""
        cmake_content = '''
add_executable(myapp main.cc)

target_link_libraries(myapp PRIVATE lib1 lib2 lib3)
'''
        targets = self.parser.parse(cmake_content)
        assert len(targets) == 1
        assert "lib1" in targets[0].private_deps
        assert "lib2" in targets[0].deps
        assert "lib3" in targets[0].deps

    def test_parse_with_custom_target(self) -> None:
        """Test parsing add_custom_target."""
        cmake_content = '''
add_custom_target(my_custom_target ALL
    COMMAND echo "Hello"
    COMMAND echo "World"
)
'''
        targets = self.parser.parse(cmake_content)
        assert len(targets) == 1
        assert targets[0].type == TargetType.ACTION


class TestGNGeneratorAdvanced:
    """Advanced tests for GN generator."""

    def setup_method(self) -> None:
        self.generator = GNGenerator()

    def test_generate_action_with_script(self) -> None:
        """Test generating action with script."""
        target = Target(
            name="gen_code",
            type=TargetType.ACTION,
            script="//tools/gen.py",
            inputs=["input.txt"],
            outputs=["output.cc"],
            deps=[":dep1"],
        )
        result = self.generator.generate(target)
        assert 'action("gen_code")' in result
        assert 'script = "//tools/gen.py"' in result
        assert 'inputs = [' in result
        assert 'outputs = [' in result

    def test_generate_with_testonly(self) -> None:
        """Test generating with testonly flag."""
        target = Target(
            name="test_runner",
            type=TargetType.EXECUTABLE,
            sources=["test.cc"],
            testonly=True,
        )
        result = self.generator.generate(target)
        assert "testonly = true" in result

    def test_generate_with_configs(self) -> None:
        """Test generating with configs."""
        target = Target(
            name="myapp",
            type=TargetType.EXECUTABLE,
            sources=["main.cc"],
            configs=[":debug", ":sanitizers"],
        )
        result = self.generator.generate(target)
        assert 'configs = [' in result
        assert '":debug"' in result
        assert '":sanitizers"' in result

    def test_generate_group(self) -> None:
        """Test generating group target."""
        target = Target(
            name="mygroup",
            type=TargetType.GROUP,
            deps=[":lib1", ":lib2"],
        )
        result = self.generator.generate(target)
        assert 'group("mygroup")' in result
        assert ":lib1" in result
        assert ":lib2" in result

    def test_generate_source_set(self) -> None:
        """Test generating source_set target."""
        target = Target(
            name="core",
            type=TargetType.SOURCE_SET,
            sources=["core.cc", "utils.cc"],
            headers=["core.h", "utils.h"],
        )
        result = self.generator.generate(target)
        assert 'source_set("core")' in result
        assert "core.cc" in result
        assert "core.h" in result


class TestCMakeGeneratorAdvanced:
    """Advanced tests for CMake generator."""

    def setup_method(self) -> None:
        self.generator = CMakeGenerator()

    def test_generate_object_library(self) -> None:
        """Test generating OBJECT library."""
        target = Target(
            name="core",
            type=TargetType.SOURCE_SET,
            sources=["core.cc", "utils.cc"],
        )
        result = self.generator.generate(target)
        assert "add_library(core OBJECT" in result
        assert "core.cc" in result

    def test_generate_interface_library(self) -> None:
        """Test generating INTERFACE library."""
        target = Target(
            name="myinterface",
            type=TargetType.GROUP,
            include_dirs=["/path/to/include"],
        )
        result = self.generator.generate(target)
        assert "add_library(myinterface INTERFACE)" in result

    def test_generate_with_compile_options(self) -> None:
        """Test generating with compile options."""
        target = Target(
            name="myapp",
            type=TargetType.EXECUTABLE,
            sources=["main.cc"],
            compile_flags=["-Wall", "-O3", "-std=c++17"],
        )
        result = self.generator.generate(target)
        assert "target_compile_options" in result
        assert "-Wall" in result

    def test_generate_custom_target(self) -> None:
        """Test generating custom target (action)."""
        target = Target(
            name="generate_code",
            type=TargetType.ACTION,
        )
        result = self.generator.generate(target)
        assert "add_custom_target" in result


class TestConverterAdvanced:
    """Advanced tests for converter."""

    def setup_method(self) -> None:
        self.converter = Converter()

    def test_roundtrip_with_action(self) -> None:
        """Test roundtrip conversion with action target."""
        gn_content = '''
action("gen") {
  sources = ["gen.py"]
}
'''
        cmake = self.converter.convert(gn_content, ConversionMode.GN_TO_CMAKE)
        roundtrip_gn = self.converter.convert(cmake, ConversionMode.CMAKE_TO_GN)

        assert 'action("gen")' in roundtrip_gn

    def test_convert_with_visibility(self) -> None:
        """Test conversion with dependency visibility."""
        gn_content = '''
static_library("mylib") {
  sources = ["lib.cc"]
  public_deps = [":base"]
  private_deps = [":utils"]
}
'''
        cmake = self.converter.convert(gn_content, ConversionMode.GN_TO_CMAKE)
        assert "target_link_libraries" in cmake

    def test_preserve_output_name(self) -> None:
        """Test that output_name is preserved during conversion."""
        gn_content = '''
executable("myapp") {
  sources = ["main.cc"]
  output_name = "my_application"
}
'''
        cmake = self.converter.convert(gn_content, ConversionMode.GN_TO_CMAKE)
        assert "OUTPUT_NAME" in cmake
        assert "my_application" in cmake


class TestConfigurationFile:
    """Tests for configuration file handling."""

    def test_load_default_config(self) -> None:
        """Test loading default configuration."""
        from gncmake_bridge import GNCMakeConfig

        config = GNCMakeConfig()
        assert isinstance(config, GNCMakeConfig)

    def test_config_from_dict(self) -> None:
        """Test creating config from dictionary."""
        from gncmake_bridge import GNCMakeConfig

        data = {
            "project": {"name": "test_project", "gn_root": "src"},
            "conversion": {"mode": "gn_to_cmake", "preserve_structure": True},
        }
        config = GNCMakeConfig.from_dict(data)
        assert config.project.name == "test_project"
        assert config.project.gn_root == "src"

    def test_config_to_dict(self) -> None:
        """Test converting config to dictionary."""
        from gncmake_bridge import GNCMakeConfig

        config = GNCMakeConfig()
        config.project.name = "myproject"
        data = config.to_dict()

        assert data["project"]["name"] == "myproject"

    def test_load_config_from_file(self) -> None:
        """Test loading configuration from TOML file."""
        from gncmake_bridge import load_config

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".toml", delete=False
        ) as f:
            f.write("""
[project]
name = "test_project"
gn_root = "."

[conversion]
mode = "gn_to_cmake"
preserve_structure = true
""")
            f.flush()

            config = load_config(f.name)
            assert config.project.name == "test_project"
            assert config.conversion.mode == "gn_to_cmake"

            Path(f.name).unlink()


class TestEdgeCases:
    """Edge case tests."""

    def setup_method(self) -> None:
        self.converter = Converter()

    def test_empty_input(self) -> None:
        """Test handling empty input."""
        result = self.converter.convert("", ConversionMode.GN_TO_CMAKE)
        assert "cmake_minimum_required" in result

    def test_whitespace_only(self) -> None:
        """Test handling whitespace-only input."""
        result = self.converter.convert("   \n\n   ", ConversionMode.GN_TO_CMAKE)
        assert "cmake_minimum_required" in result

    def test_comments_only(self) -> None:
        """Test handling comments-only input."""
        gn_content = '''
# This is a comment
# Another comment
'''
        result = self.converter.convert(gn_content, ConversionMode.GN_TO_CMAKE)
        assert "cmake_minimum_required" in result

    def test_mixed_newlines(self) -> None:
        """Test handling mixed line endings."""
        gn_content = "executable(\"test\") {\r\n  sources = [\"main.cc\"]\r\n}\r\n"
        targets = GNParser().parse(gn_content)
        assert len(targets) == 1
        assert targets[0].name == "test"
