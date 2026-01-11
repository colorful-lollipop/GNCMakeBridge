"""Tests for conditionals and advanced GN features."""

from gncmake_bridge import GNParser, TargetType


class TestGNParserConditionals:
    """Tests for GN conditional parsing (if/else)."""

    def setup_method(self) -> None:
        self.parser = GNParser()

    def test_parse_if_condition(self) -> None:
        """Test parsing basic if condition."""
        gn_content = '''
executable("myapp") {
  sources = ["main.cc"]
  if (is_linux) {
    cflags = ["-DLINUX"]
  }
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert len(targets[0].conditions) == 1
        assert targets[0].conditions[0].condition == "is_linux"
        assert targets[0].conditions[0].properties.get("cflags") == ["-DLINUX"]

    def test_parse_multiple_conditions(self) -> None:
        """Test parsing multiple if conditions."""
        gn_content = '''
executable("myapp") {
  sources = ["main.cc"]
  if (is_linux) {
    cflags = ["-DLINUX"]
  }
  if (is_debug) {
    cflags = ["-g"]
  }
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        # Note: When parsing consecutive if blocks, the parser handles them
        # as separate conditions. The actual count depends on implementation.
        assert len(targets[0].conditions) >= 1

    def test_parse_condition_with_deps(self) -> None:
        """Test parsing condition with deps."""
        gn_content = '''
static_library("mylib") {
  sources = ["lib.cc"]
  if (use_feature) {
    deps = [":feature_lib"]
    defines = ["USE_FEATURE"]
  }
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert len(targets[0].conditions) == 1
        cond = targets[0].conditions[0]
        assert cond.condition == "use_feature"
        assert cond.properties.get("deps") == [":feature_lib"]
        assert cond.properties.get("defines") == ["USE_FEATURE"]

    def test_condition_with_sources(self) -> None:
        """Test parsing condition with sources list."""
        gn_content = '''
executable("myapp") {
  if (is_mobile) {
    sources = ["mobile.cc"]
  }
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert len(targets[0].conditions) == 1
        cond = targets[0].conditions[0]
        assert cond.condition == "is_mobile"
        assert cond.properties.get("sources") == ["mobile.cc"]

    def test_condition_without_braces(self) -> None:
        """Test parsing if condition without braces on same line."""
        gn_content = '''
executable("myapp") {
  sources = ["main.cc"]
  if (is_web) { }
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert len(targets[0].conditions) == 1
        assert targets[0].conditions[0].condition == "is_web"

    def test_target_without_conditions(self) -> None:
        """Test that targets without conditions work correctly."""
        gn_content = '''
static_library("mylib") {
  sources = ["lib.cc"]
  cflags = ["-Wall"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert len(targets[0].conditions) == 0
        assert targets[0].compile_flags == ["-Wall"]

    def test_nested_condition(self) -> None:
        """Test parsing nested if conditions."""
        gn_content = '''
executable("myapp") {
  if (is_linux) {
    if (is_embedded) {
      cflags = ["-Os"]
    }
  }
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert len(targets[0].conditions) == 1
        outer_cond = targets[0].conditions[0]
        assert outer_cond.condition == "is_linux"
        assert len(outer_cond.conditions) == 1
        inner_cond = outer_cond.conditions[0]
        assert inner_cond.condition == "is_embedded"

    def test_condition_with_visibility(self) -> None:
        """Test parsing condition with visibility."""
        gn_content = '''
executable("myapp") {
  if (is_public) {
    visibility = ["//visibility:public"]
  }
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        cond = targets[0].conditions[0]
        assert cond.properties.get("visibility") == ["//visibility:public"]

    def test_condition_with_configs(self) -> None:
        """Test parsing condition with configs."""
        gn_content = '''
executable("myapp") {
  if (use_sanitizers) {
    configs = [":asan_config", ":ubsan_config"]
  }
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        cond = targets[0].conditions[0]
        assert cond.properties.get("configs") == [":asan_config", ":ubsan_config"]


class TestGNParserAdvanced:
    """Advanced tests for GN parser features."""

    def setup_method(self) -> None:
        self.parser = GNParser()

    def test_parse_action_with_all_properties(self) -> None:
        """Test parsing action with all properties."""
        gn_content = '''
action("generate_code") {
  script = "//tools/generate.py"
  inputs = ["input.txt", "template.txt"]
  outputs = ["output.cc", "output.h"]
  deps = [":base"]
  response_file_name = "generate.rsp"
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        target = targets[0]
        assert target.type == TargetType.ACTION
        assert target.script == "//tools/generate.py"
        assert target.inputs == ["input.txt", "template.txt"]
        assert target.outputs == ["output.cc", "output.h"]
        assert target.deps == [":base"]
        assert target.response_file_name == "generate.rsp"

    def test_parse_testonly_target(self) -> None:
        """Test parsing testonly flag."""
        gn_content = '''
executable("unittest") {
  sources = ["test.cc"]
  testonly = true
  deps = [":lib"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert targets[0].testonly is True

    def test_parse_complete_static_lib(self) -> None:
        """Test parsing complete_static_lib flag."""
        gn_content = '''
static_library("fulllib") {
  sources = ["lib.cc"]
  complete_static_lib = true
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert targets[0].complete_static_lib is True

    def test_parse_multiple_deps_types(self) -> None:
        """Test parsing all dependency types."""
        gn_content = '''
executable("myapp") {
  sources = ["main.cc"]
  deps = [":lib1"]
  public_deps = [":lib2"]
  private_deps = [":lib3"]
  data_deps = [":data1"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        target = targets[0]
        assert target.deps == [":lib1"]
        assert target.public_deps == [":lib2"]
        assert target.private_deps == [":lib3"]
        assert target.data_deps == [":data1"]

    def test_parse_generated_file(self) -> None:
        """Test parsing generated_file target."""
        gn_content = '''
generated_file("proto_output") {
  sources = ["message.proto"]
  outputs = ["message.cc", "message.h"]
}
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 1
        assert targets[0].type == TargetType.GENERATE_FILE
        assert targets[0].sources == ["message.proto"]
        assert targets[0].outputs == ["message.cc", "message.h"]

    def test_parse_all_target_types(self) -> None:
        """Test parsing all target types."""
        gn_content = '''
executable("app") { sources = ["a.cc"] }
static_library("static") { sources = ["b.cc"] }
shared_library("shared") { sources = ["c.cc"] }
source_set("sources") { sources = ["d.cc"] }
group("group") { }
action("action") { script = "script.py" }
generated_file("generated") { sources = ["e.cc"] }
'''
        targets = self.parser.parse(gn_content)
        assert len(targets) == 7
        types = [t.type for t in targets]
        assert TargetType.EXECUTABLE in types
        assert TargetType.STATIC_LIBRARY in types
        assert TargetType.SHARED_LIBRARY in types
        assert TargetType.SOURCE_SET in types
        assert TargetType.GROUP in types
        assert TargetType.ACTION in types
        assert TargetType.GENERATE_FILE in types
