# SnowNavi Pose Analyzer

一个专为滑雪教练和运动分析师设计的人体姿态检测应用程序，基于Python和PySide6开发。

## 🚀 快速开始

### 自动环境配置（推荐）

```bash
# Python脚本版本（跨平台）
python scripts/setup_environment.py

# Shell脚本版本（macOS/Linux）
./scripts/setup_environment.sh
```

### 手动配置

```bash
# 1. 创建虚拟环境
python3 -m venv pose_detection_env

# 2. 激活虚拟环境
source pose_detection_env/bin/activate  # macOS/Linux
# 或
pose_detection_env\Scripts\activate     # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动应用
python pose_detection_app_pyside6.py
```

## ✨ 主要功能

- 🎥 **智能视频分析**: 支持多种格式，实时姿态检测
- 🔄 **双视频比较**: 并排对比分析，智能布局适配
- 👥 **多人检测**: 自动识别并选择特定人物追踪
- 🎨 **自定义样式**: 可调节颜色、粗细、形状等视觉效果
- 📤 **视频导出**: 保存带姿态检测的分析结果
- 🔧 **配置管理**: 保存和加载自定义设置
- 💧 **水印功能**: 支持文字和图片水印

## 📁 项目结构

```
snownaviCoach/
├── pose_detection_app_pyside6.py  # 主应用程序
├── requirements.txt                # 依赖包列表
├── docs/                          # 📚 文档目录
│   ├── README.md                  # 详细说明文档
│   ├── QUICK_START.md            # 快速开始指南
│   ├── TROUBLESHOOTING.md        # 故障排除指南
│   └── guides/                   # 技术指南
│       ├── STYLE_UNIFICATION_GUIDE.md
│       └── LAYOUT_OPTIMIZATION_GUIDE.md
├── scripts/                      # 🔧 脚本目录
│   ├── setup_environment.py     # 环境配置脚本（Python）
│   ├── setup_environment.sh     # 环境配置脚本（Shell）
│   └── create_logo.py           # Logo生成脚本
├── assets/                       # 🎨 资源文件
│   ├── snownavi_logo.png        # 应用程序图标
│   └── pose_landmarker_full.task # MediaPipe模型文件
├── tests/                        # 🧪 测试文件
│   ├── test_*.py                # 各种功能测试
│   └── verify_*.py              # 验证脚本
└── pose_detection_env/          # 🐍 虚拟环境目录
```

## 🛠️ 技术栈

- **Python 3.8+** - 核心语言
- **PySide6** - 现代GUI框架
- **OpenCV** - 视频处理
- **MediaPipe** - 人体姿态检测
- **NumPy** - 数值计算
- **Pillow** - 图像处理

## 📖 文档

- **[详细说明文档](docs/README.md)** - 完整功能介绍和使用指南
- **[快速开始指南](docs/QUICK_START.md)** - 立即上手使用
- **[故障排除指南](docs/TROUBLESHOOTING.md)** - 常见问题解决方案
- **[样式统一化指南](docs/guides/STYLE_UNIFICATION_GUIDE.md)** - UI样式技术文档
- **[布局优化指南](docs/guides/LAYOUT_OPTIMIZATION_GUIDE.md)** - 界面布局优化说明

## 🎯 系统要求

- **操作系统**: macOS 10.14+, Windows 10+, Linux
- **Python版本**: 3.8+
- **内存**: 建议4GB以上
- **处理器**: 支持AVX指令集的现代CPU

## 🔧 开发

### 运行测试

```bash
# 激活虚拟环境
source pose_detection_env/bin/activate

# 运行功能测试
python tests/test_pose_detection.py

# 运行性能测试
python tests/test_performance.py

# 运行UI测试
python tests/test_ui_responsiveness.py
```

### 环境管理

```bash
# 重新配置环境
python scripts/setup_environment.py

# 检查依赖
pip list

# 更新依赖
pip install -r requirements.txt --upgrade
```

## 🤝 贡献

欢迎提交Issue和Pull Request来改进项目。

## 📄 许可证

本项目仅供学习和研究使用。

## 📞 支持

如有问题或建议，请通过GitHub Issues联系。

---

**SnowNavi 开发团队** | 2025-07-04
