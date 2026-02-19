#!/usr/bin/env python3
"""
Fill 项目开发环境检查脚本

在开始开发之前运行此脚本，确保环境配置正确。
"""

import os
import sys
from pathlib import Path


def check_python_version():
    """检查 Python 版本"""
    print("🐍 检查 Python 版本...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print("   需要 Python 3.11+")
        return False


def check_dependencies():
    """检查依赖是否安装"""
    print("\n📦 检查依赖...")
    required_packages = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pytest",
        "playwright",
        "openpyxl",
        "python-docx",
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} 未安装")
            missing.append(package)

    if missing:
        print(f"\n⚠️  缺少依赖: {', '.join(missing)}")
        print("   运行: pip install -r requirements.txt")
        return False
    return True


def check_project_structure():
    """检查项目结构是否完整"""
    print("\n📁 检查项目结构...")

    required_files = [
        # 核心代码
        "src/main.py",
        "src/models/file.py",
        "src/models/template.py",
        "src/models/mapping.py",
        "src/models/job.py",
        "src/repositories/file_repository.py",
        "src/repositories/template_repository.py",
        "src/repositories/mapping_repository.py",
        "src/repositories/job_repository.py",
        "src/services/file_storage.py",
        "src/services/csv_parser.py",
        "src/services/excel_parser.py",
        "src/services/docx_generator.py",
        "src/services/excel_template_filler.py",
        "src/services/batch_processor.py",
        # 前端页面
        "src/static/index.html",
        "src/static/templates.html",
        "src/static/mapping.html",
        "src/static/processing.html",
        # 文档
        "PROJECT_CONTEXT.md",
        "QUICK_REFERENCE.md",
        "README.md",
        # 配置
        "pyproject.toml",
        "requirements.txt",
    ]

    missing = []
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} 缺失")
            missing.append(file_path)

    if missing:
        print(f"\n⚠️  缺少 {len(missing)} 个文件")
        return False
    return True


def check_api_endpoints():
    """检查 main.py 是否包含所有必需的 API 端点"""
    print("\n🔌 检查 API 端点...")

    main_py = Path("src/main.py")
    if not main_py.exists():
        print("❌ src/main.py 不存在")
        return False

    content = main_py.read_text()

    required_endpoints = [
        '@app.get("/")',
        '@app.post("/api/v1/upload")',
        '@app.get("/api/v1/files")',
        '@app.get("/api/v1/templates")',
        '@app.post("/api/v1/templates")',
        '@app.post("/api/v1/parse")',
        '@app.post("/api/v1/suggest-mapping")',
        '@app.post("/api/v1/mappings")',
        '@app.post("/api/v1/jobs")',
    ]

    missing = []
    for endpoint in required_endpoints:
        if endpoint in content:
            print(f"✅ {endpoint}")
        else:
            print(f"❌ {endpoint} 缺失")
            missing.append(endpoint)

    if missing:
        print(f"\n⚠️  警告: 缺少 {len(missing)} 个 API 端点")
        print("   这可能是简化版本！请阅读 PROJECT_CONTEXT.md")
        return False
    return True


def check_documentation():
    """检查文档是否完整"""
    print("\n📚 检查文档...")

    required_docs = [
        ("PROJECT_CONTEXT.md", "项目完整上下文"),
        ("QUICK_REFERENCE.md", "快速参考"),
        ("README.md", "项目说明"),
    ]

    for doc_file, description in required_docs:
        if Path(doc_file).exists():
            print(f"✅ {doc_file} ({description})")
        else:
            print(f"⚠️  {doc_file} 缺失")

    # 提示阅读完整上下文
    if Path("PROJECT_CONTEXT.md").exists():
        print("\n💡 提示: 开发前请阅读 PROJECT_CONTEXT.md 获取完整上下文")
    return True


def run_tests():
    """运行测试验证"""
    print("\n🧪 运行测试...")
    print("   (这可能需要几分钟)")

    import subprocess
    try:
        result = subprocess.run(
            ["python", "-m", "pytest", "tests/unit", "tests/integration",
             "-v", "--tb=no", "-q"],
            capture_output=True,
            text=True,
            timeout=120
        )

        if result.returncode == 0:
            # 提取测试统计
            lines = result.stdout.split('\n')
            for line in lines:
                if 'passed' in line:
                    print(f"✅ {line.strip()}")
                    break
            return True
        else:
            print(f"❌ 测试失败")
            print("   运行: pytest tests/unit tests/integration -v 查看详情")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  测试超时")
        return False
    except Exception as e:
        print(f"⚠️  无法运行测试: {e}")
        return False


def main():
    """主检查流程"""
    print("=" * 60)
    print("Fill 项目开发环境检查")
    print("=" * 60)

    checks = [
        check_python_version,
        check_dependencies,
        check_project_structure,
        check_api_endpoints,
        check_documentation,
    ]

    results = []
    for check in checks:
        try:
            result = check()
            results.append(result)
        except Exception as e:
            print(f"❌ 检查失败: {e}")
            results.append(False)

    # 总结
    print("\n" + "=" * 60)
    print("检查总结")
    print("=" * 60)

    passed = sum(results)
    total = len(results)

    if all(results):
        print(f"✅ 所有检查通过！({passed}/{total})")
        print("\n🎉 环境配置正确，可以开始开发了！")
        print("\n下一步:")
        print("  1. 阅读 PROJECT_CONTEXT.md 了解项目全貌")
        print("  2. 运行 pytest 确保测试通过")
        print("  3. 开始开发，遵循 QUICK_REFERENCE.md 的规范")
        return 0
    else:
        print(f"⚠️  {passed}/{total} 检查通过")
        print("\n请解决上述问题后再开始开发。")
        print("\n常见问题:")
        print("  • 依赖缺失 → pip install -r requirements.txt")
        print("  • 文件缺失 → 可能是简化版本，请重新克隆")
        print("  • API 端点缺失 → 必须使用完整版本")
        return 1


if __name__ == "__main__":
    sys.exit(main())
