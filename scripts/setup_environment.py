#!/usr/bin/env python3
"""
SnowNavi Pose Analyzer - 环境配置脚本

这个脚本帮助开发人员快速配置运行环境，包括：
1. 检查Python版本
2. 创建虚拟环境
3. 安装依赖包
4. 验证安装
5. 提供启动指令

使用方法：
    python scripts/setup_environment.py

作者: SnowNavi 开发团队
日期: 2025-07-04
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

class Colors:
    """控制台颜色输出"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_step(step_num, title, description=""):
    """打印步骤信息"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}步骤 {step_num}: {title}{Colors.END}")
    if description:
        print(f"{Colors.YELLOW}{description}{Colors.END}")

def print_success(message):
    """打印成功信息"""
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    """打印错误信息"""
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_warning(message):
    """打印警告信息"""
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.END}")

def check_python_version():
    """检查Python版本"""
    print_step(1, "检查Python版本", "确保Python版本 >= 3.8")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print_error(f"Python版本过低: {version.major}.{version.minor}")
        print_error("请安装Python 3.8或更高版本")
        return False
    
    print_success(f"Python版本: {version.major}.{version.minor}.{version.micro}")
    return True

def get_project_root():
    """获取项目根目录"""
    current_dir = Path(__file__).parent.parent
    return current_dir.resolve()

def create_virtual_environment():
    """创建虚拟环境"""
    print_step(2, "创建虚拟环境", "创建独立的Python环境")
    
    project_root = get_project_root()
    venv_path = project_root / "pose_detection_env"
    
    if venv_path.exists():
        print_warning("虚拟环境已存在，跳过创建")
        return True
    
    try:
        subprocess.run([
            sys.executable, "-m", "venv", str(venv_path)
        ], check=True, capture_output=True)
        print_success(f"虚拟环境创建成功: {venv_path}")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"创建虚拟环境失败: {e}")
        return False

def get_activation_command():
    """获取虚拟环境激活命令"""
    project_root = get_project_root()
    
    if platform.system() == "Windows":
        return str(project_root / "pose_detection_env" / "Scripts" / "activate.bat")
    else:
        return f"source {project_root}/pose_detection_env/bin/activate"

def install_dependencies():
    """安装依赖包"""
    print_step(3, "安装依赖包", "安装项目所需的Python包")
    
    project_root = get_project_root()
    requirements_file = project_root / "requirements.txt"
    
    if not requirements_file.exists():
        print_error("requirements.txt 文件不存在")
        return False
    
    # 获取虚拟环境中的pip路径
    if platform.system() == "Windows":
        pip_path = project_root / "pose_detection_env" / "Scripts" / "pip"
    else:
        pip_path = project_root / "pose_detection_env" / "bin" / "pip"
    
    try:
        # 升级pip
        subprocess.run([
            str(pip_path), "install", "--upgrade", "pip"
        ], check=True, capture_output=True)
        
        # 安装依赖
        subprocess.run([
            str(pip_path), "install", "-r", str(requirements_file)
        ], check=True, capture_output=True)
        
        print_success("依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"安装依赖包失败: {e}")
        return False

def verify_installation():
    """验证安装"""
    print_step(4, "验证安装", "检查关键依赖包是否正确安装")
    
    project_root = get_project_root()
    
    # 获取虚拟环境中的python路径
    if platform.system() == "Windows":
        python_path = project_root / "pose_detection_env" / "Scripts" / "python"
    else:
        python_path = project_root / "pose_detection_env" / "bin" / "python"
    
    # 检查关键包
    packages_to_check = [
        ("PySide6", "import PySide6; print(PySide6.__version__)"),
        ("OpenCV", "import cv2; print(cv2.__version__)"),
        ("MediaPipe", "import mediapipe; print(mediapipe.__version__)"),
        ("NumPy", "import numpy; print(numpy.__version__)"),
        ("Pillow", "import PIL; print(PIL.__version__)")
    ]
    
    all_success = True
    for package_name, test_code in packages_to_check:
        try:
            result = subprocess.run([
                str(python_path), "-c", test_code
            ], check=True, capture_output=True, text=True)
            version = result.stdout.strip()
            print_success(f"{package_name}: {version}")
        except subprocess.CalledProcessError:
            print_error(f"{package_name}: 安装失败或版本检查失败")
            all_success = False
    
    return all_success

def print_usage_instructions():
    """打印使用说明"""
    print_step(5, "使用说明", "如何启动应用程序")
    
    activation_cmd = get_activation_command()
    project_root = get_project_root()
    
    print(f"\n{Colors.BOLD}🚀 环境配置完成！{Colors.END}")
    print(f"\n{Colors.BOLD}启动应用程序：{Colors.END}")
    print(f"1. 激活虚拟环境：")
    print(f"   {Colors.GREEN}{activation_cmd}{Colors.END}")
    print(f"2. 启动应用：")
    print(f"   {Colors.GREEN}python pose_detection_app_pyside6.py{Colors.END}")
    
    print(f"\n{Colors.BOLD}或者使用一键启动：{Colors.END}")
    if platform.system() == "Windows":
        print(f"   {Colors.GREEN}{project_root}/pose_detection_env/Scripts/activate && python pose_detection_app_pyside6.py{Colors.END}")
    else:
        print(f"   {Colors.GREEN}cd {project_root} && source pose_detection_env/bin/activate && python pose_detection_app_pyside6.py{Colors.END}")
    
    print(f"\n{Colors.BOLD}📚 文档位置：{Colors.END}")
    print(f"   主要文档: {Colors.BLUE}docs/README.md{Colors.END}")
    print(f"   快速开始: {Colors.BLUE}docs/QUICK_START.md{Colors.END}")
    print(f"   故障排除: {Colors.BLUE}docs/TROUBLESHOOTING.md{Colors.END}")

def main():
    """主函数"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("=" * 60)
    print("    SnowNavi Pose Analyzer - 环境配置脚本")
    print("=" * 60)
    print(f"{Colors.END}")
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 创建虚拟环境
    if not create_virtual_environment():
        sys.exit(1)
    
    # 安装依赖包
    if not install_dependencies():
        sys.exit(1)
    
    # 验证安装
    if not verify_installation():
        print_warning("某些包验证失败，但可能仍然可以运行")
    
    # 打印使用说明
    print_usage_instructions()
    
    print(f"\n{Colors.BOLD}{Colors.GREEN}🎉 环境配置完成！{Colors.END}")

if __name__ == "__main__":
    main()
