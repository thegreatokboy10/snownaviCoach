#!/bin/bash

# SnowNavi Pose Analyzer - 环境配置脚本 (Shell版本)
# 
# 这个脚本帮助快速配置运行环境
# 
# 使用方法：
#   chmod +x scripts/setup_environment.sh
#   ./scripts/setup_environment.sh
#
# 作者: SnowNavi 开发团队
# 日期: 2025-07-04

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# 打印函数
print_step() {
    echo -e "\n${BOLD}${BLUE}步骤 $1: $2${NC}"
    if [ ! -z "$3" ]; then
        echo -e "${YELLOW}$3${NC}"
    fi
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 检查Python版本
check_python() {
    print_step 1 "检查Python版本" "确保Python版本 >= 3.8"
    
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        return 1
    fi
    
    python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    print_success "Python版本: $python_version"
    return 0
}

# 创建虚拟环境
create_venv() {
    print_step 2 "创建虚拟环境" "创建独立的Python环境"
    
    if [ -d "pose_detection_env" ]; then
        print_warning "虚拟环境已存在，跳过创建"
        return 0
    fi
    
    python3 -m venv pose_detection_env
    if [ $? -eq 0 ]; then
        print_success "虚拟环境创建成功"
        return 0
    else
        print_error "虚拟环境创建失败"
        return 1
    fi
}

# 安装依赖
install_deps() {
    print_step 3 "安装依赖包" "安装项目所需的Python包"
    
    if [ ! -f "requirements.txt" ]; then
        print_error "requirements.txt 文件不存在"
        return 1
    fi
    
    # 激活虚拟环境
    source pose_detection_env/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    pip install -r requirements.txt
    
    if [ $? -eq 0 ]; then
        print_success "依赖包安装成功"
        return 0
    else
        print_error "依赖包安装失败"
        return 1
    fi
}

# 验证安装
verify_installation() {
    print_step 4 "验证安装" "检查关键依赖包是否正确安装"
    
    # 激活虚拟环境
    source pose_detection_env/bin/activate
    
    # 检查关键包
    packages=("PySide6" "cv2" "mediapipe" "numpy" "PIL")
    
    for package in "${packages[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            version=$(python3 -c "import $package; print(getattr($package, '__version__', 'unknown'))" 2>/dev/null)
            print_success "$package: $version"
        else
            print_error "$package: 安装失败"
        fi
    done
}

# 打印使用说明
print_usage() {
    print_step 5 "使用说明" "如何启动应用程序"
    
    echo -e "\n${BOLD}🚀 环境配置完成！${NC}"
    echo -e "\n${BOLD}启动应用程序：${NC}"
    echo -e "1. 激活虚拟环境："
    echo -e "   ${GREEN}source pose_detection_env/bin/activate${NC}"
    echo -e "2. 启动应用："
    echo -e "   ${GREEN}python pose_detection_app_pyside6.py${NC}"
    
    echo -e "\n${BOLD}或者使用一键启动：${NC}"
    echo -e "   ${GREEN}source pose_detection_env/bin/activate && python pose_detection_app_pyside6.py${NC}"
    
    echo -e "\n${BOLD}📚 文档位置：${NC}"
    echo -e "   主要文档: ${BLUE}docs/README.md${NC}"
    echo -e "   快速开始: ${BLUE}docs/QUICK_START.md${NC}"
    echo -e "   故障排除: ${BLUE}docs/TROUBLESHOOTING.md${NC}"
}

# 主函数
main() {
    echo -e "${BOLD}${BLUE}"
    echo "============================================================"
    echo "    SnowNavi Pose Analyzer - 环境配置脚本"
    echo "============================================================"
    echo -e "${NC}"
    
    # 检查Python
    if ! check_python; then
        exit 1
    fi
    
    # 创建虚拟环境
    if ! create_venv; then
        exit 1
    fi
    
    # 安装依赖
    if ! install_deps; then
        exit 1
    fi
    
    # 验证安装
    verify_installation
    
    # 打印使用说明
    print_usage
    
    echo -e "\n${BOLD}${GREEN}🎉 环境配置完成！${NC}"
}

# 运行主函数
main
