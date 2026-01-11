# GN ↔ CMake 双向转换工具项目开发白皮书（总结版）

---

## 1. 项目概述

**核心目标**: 开发自动化工具，实现 GN 与 CMake 构建系统的双向转换，降低 Chromium 等大型项目的开发门槛。

**关键价值**:
- 降低新贡献者学习成本（GN → 主流 CMake）
- 提升 IDE 集成体验（CLion、VSCode 原生支持）
- 支持混合构建（遗留 CMake 项目 + 新 GN 模块）
- 促进构建系统迁移与现代化

---

## 2. 技术架构（三层设计）

```
┌─────────────────────────────────────┐
│     用户接口层                       │
│  CLI / API / IDE插件 / Web服务      │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     核心转换引擎                     │
│  ┌──────────┐      ┌──────────┐    │
│  │GN Parser │◄────►│   IR    │    │
│  └──────────┘      └────┬─────┘    │
│                         │           │
│  ┌──────────┐          │           │
│  │CMake Gen │◄─────────┘           │
│  └──────────┘                       │
└─────────────────────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     基础设施层                       │
│  配置系统 / 插件框架 / 工具链抽象   │
└─────────────────────────────────────┘
```

**中间表示（IR）核心结构**:
```python
Target(
    name, type,  # 目标名称和类型
    sources, headers,  # 源文件
    dependencies,  # 依赖关系图
    compile_flags, link_flags,  # 编译链接选项
    visibility, metadata  # 可见性和元数据
)
```

**关键转换流程**:
1. **解析**: GN/CMake → AST → IR
2. **规范化**: 语义分析、依赖解析、类型推断
3. **生成**: IR → CMake/GN 代码（模板化输出）

---

## 3. 核心功能特性

### 3.1 基础转换支持

| GN 概念 | CMake 映射 | 复杂度 |
|---------|-----------|--------|
| `executable()` | `add_executable()` | 简单 |
| `static_library()` | `add_library(STATIC)` | 简单 |
| `shared_library()` | `add_library(SHARED)` | 中等 |
| `source_set()` | `add_library(OBJECT)` | 中等 |
| `action()` | `add_custom_command()` | 复杂 |
| `template{}` | CMake 函数 + 封装 | 复杂 |
| `config()` | `target_compile_options()` | 中等 |

### 3.2 高级特性

**依赖关系处理**:
- `deps` → `target_link_libraries(PRIVATE)`
- `public_deps` → `target_link_libraries(PUBLIC)`
- `data_deps` → 自定义属性传递

**条件编译**:
```python
# GN: if (is_linux) { sources += ["linux.cc"] }
# CMake: if(LINUX) list(APPEND sources linux.cc) endif()
```

**工具链抽象**:
```python
Toolchain(
    c_compiler, cxx_compiler,
    ar, linker,
    sysroot, target_triple,
    cmake_toolchain_file  # 映射路径
)
```

### 3.3 混合构建桥接

**场景**: CMake 主项目引用 GN 子模块
```cmake
# 自动生成的桥接代码
gn_import_target(
    GN_TARGET "//base:base"
    CMAKE_TARGET base_from_gn
    BUILD_DIR ${GN_BUILD_DIR}
)
target_link_libraries(my_app PRIVATE base_from_gn)
```

---

## 4. 配置文件示例（gncmake.toml）

```toml
[project]
name = "chromium_subset"
gn_root = "."
output_dir = "cmake_output"

[conversion]
mode = "gn_to_cmake"
preserve_structure = true
human_readable = true

[targets]
include = ["//base/...", "//net/..."]
exclude = ["//third_party/...", "*_unittest"]

[cmake]
minimum_version = "3.20"
generator = "Ninja"
use_ccache = true

[cmake.options]
CMAKE_CXX_STANDARD = 17
BUILD_SHARED_LIBS = false

[dependencies.external_mapping]
"//third_party/protobuf:protobuf" = "protobuf::libprotobuf"
"//third_party/googletest:gtest" = "GTest::gtest"
```

---

## 5. 开发计划（18个月）

### Phase 1: 基础架构（3个月）
- ✅ 核心框架 + GN Parser
- ✅ 简单项目转换（<100 targets）
- ✅ 单元测试覆盖率 >60%

### Phase 2: 功能完善（5个月）
- ✅ Action/Template 支持
- ✅ 跨平台工具链适配
- ✅ 中型项目支持（1000 targets）

### Phase 3: 双向转换（4个月）
- ✅ CMake → GN 转换
- ✅ 往返测试（roundtrip）
- ✅ 性能优化（<10分钟/大型项目）

### Phase 4: 生产化（6个月）
- ✅ IDE 集成（VSCode 插件）
- ✅ 完整文档 + 1.0 发布
- ✅ 社区运营

**人员配置**: 3-4人核心团队（架构师、解析专家、代码生成专家、测试工程师）

---

## 6. 测试策略

```python
测试金字塔:

┌─────────────┐
│ E2E 测试     │  完整项目转换（Chromium 子集）
├─────────────┤
│ 集成测试     │  多模块依赖、工具链切换
├─────────────┤
│ 单元测试     │  AST 节点、转换规则、语义分析
└─────────────┘

覆盖率目标: 代码 >80%, 分支 >70%
性能基准: 1000 targets < 30秒
```

**关键测试用例**:
- 简单项目：Hello World、单库依赖
- 中型项目：多模块、条件编译、自定义工具链
- 复杂项目：Chromium base/net（action、template、复杂依赖）

---

## 7. 风险与挑战

| 风险 | 缓解策略 |
|------|----------|
| **GN 特性无法完美映射** | 早期原型验证；提供"手动干预模式" |
| **性能瓶颈** | 增量解析；并行化；考虑 Rust 重写 |
| **Chromium 规模超预期** | 分阶段支持；限定范围（排除 WebRTC） |
| **团队成员流失** | 完善文档；代码审查；知识分享 |

---

## 8. 成功指标

**技术指标**:
- GN 核心特性覆盖率 >90%
- 自动转换成功率: 简单项目 >95%, 复杂项目 >70%
- 性能: 20000 targets < 15分钟

**社区指标**（18个月）:
- GitHub Stars >1000
- 实际使用项目 >50
- 贡献者 >20人

**业务价值**:
- 新手上手时间 -40%
- IDE 调试效率 +50%
- 年度成本节约 ~$120K（大型团队）

---

## 9. 总结

本项目通过**中间表示驱动**的架构，在保证**语义正确性**的前提下，实现 GN 与 CMake 的**双向高质量转换**。核心挑战在于处理两种构建系统的**语义差异**（如 source_set vs OBJECT 库）和**工具链抽象**。

采用**渐进式开发**策略，从简单场景到复杂项目逐步推进，配合**完善的测试体系**和**混合构建能力**，最终目标是成为 Chromium 生态和其他 GN 项目的**标准迁移工具**，同时为构建系统互操作性提供参考实现。

**下一步行动**:
1. 建立 GitHub 仓库 + CI/CD
2. 实现 MVP（支持 50 targets 项目）
3. 与 Chromium 团队建立联系
4. 发布技术博客吸引早期用户
