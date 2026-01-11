import pytest

from gncmake_bridge import GNGenerator, CMakeGenerator, Target, TargetType


class TestGNGenerator:
    def setup_method(self) -> None:
        self.generator = GNGenerator()

    def test_generate_executable(self) -> None:
        target = Target(
            name="hello",
            type=TargetType.EXECUTABLE,
            sources=["main.cc"],
            deps=[":lib1"],
        )
        result = self.generator.generate(target)
        assert 'executable("hello")' in result
        assert "main.cc" in result
        assert ":lib1" in result

    def test_generate_static_library(self) -> None:
        target = Target(
            name="mylib",
            type=TargetType.STATIC_LIBRARY,
            sources=["lib.cc"],
            headers=["lib.h"],
            public_deps=[":dep1"],
        )
        result = self.generator.generate(target)
        assert 'static_library("mylib")' in result
        assert "lib.cc" in result
        assert "lib.h" in result
        assert ":dep1" in result

    def test_generate_with_flags(self) -> None:
        target = Target(
            name="myapp",
            type=TargetType.EXECUTABLE,
            sources=["app.cc"],
            compile_flags=["-Wall", "-O2"],
            link_flags=["-lm"],
        )
        result = self.generator.generate(target)
        assert "-Wall" in result
        assert "-O2" in result
        assert "-lm" in result

    def test_generate_with_output_name(self) -> None:
        target = Target(
            name="myapp",
            type=TargetType.EXECUTABLE,
            sources=["app.cc"],
            output_name="final_executable",
        )
        result = self.generator.generate(target)
        assert 'output_name = "final_executable"' in result


class TestCMakeGenerator:
    def setup_method(self) -> None:
        self.generator = CMakeGenerator()

    def test_generate_executable(self) -> None:
        target = Target(
            name="hello",
            type=TargetType.EXECUTABLE,
            sources=["main.cc"],
        )
        result = self.generator.generate(target)
        assert "add_executable(hello" in result
        assert "main.cc" in result

    def test_generate_static_library(self) -> None:
        target = Target(
            name="mylib",
            type=TargetType.STATIC_LIBRARY,
            sources=["lib.cc"],
        )
        result = self.generator.generate(target)
        assert "add_library(mylib STATIC" in result

    def test_generate_shared_library(self) -> None:
        target = Target(
            name="myshared",
            type=TargetType.SHARED_LIBRARY,
            sources=["shared.cc"],
        )
        result = self.generator.generate(target)
        assert "add_library(myshared SHARED" in result

    def test_generate_link_libraries(self) -> None:
        target = Target(
            name="app",
            type=TargetType.EXECUTABLE,
            sources=["app.cc"],
            public_deps=["lib1"],
            private_deps=["lib2"],
        )
        result = self.generator.generate(target)
        assert "target_link_libraries(app" in result
        assert "lib1" in result
        assert "lib2" in result

    def test_generate_include_directories(self) -> None:
        target = Target(
            name="app",
            type=TargetType.EXECUTABLE,
            sources=["app.cc"],
            include_dirs=["/usr/include"],
        )
        result = self.generator.generate(target)
        assert "target_include_directories" in result
        assert "/usr/include" in result

    def test_generate_output_name(self) -> None:
        target = Target(
            name="myapp",
            type=TargetType.EXECUTABLE,
            sources=["app.cc"],
            output_name="final_app",
        )
        result = self.generator.generate(target)
        assert "OUTPUT_NAME" in result
        assert "final_app" in result
