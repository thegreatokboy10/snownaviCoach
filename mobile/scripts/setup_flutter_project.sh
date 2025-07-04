#!/bin/bash

# SnowNavi Pose Analyzer - Flutter Project Setup Script
# This script sets up the Flutter mobile project for development

set -e

echo "🏂 SnowNavi Pose Analyzer - Flutter Project Setup"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Flutter is installed
check_flutter() {
    print_status "Checking Flutter installation..."
    
    if ! command -v flutter &> /dev/null; then
        print_error "Flutter is not installed or not in PATH"
        print_status "Please install Flutter from https://flutter.dev/docs/get-started/install"
        exit 1
    fi
    
    flutter --version
    print_success "Flutter is installed"
}

# Check Flutter doctor
check_flutter_doctor() {
    print_status "Running Flutter doctor..."
    
    if flutter doctor | grep -q "No issues found"; then
        print_success "Flutter doctor - no issues found"
    else
        print_warning "Flutter doctor found some issues. Please review:"
        flutter doctor
        echo ""
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_error "Setup cancelled. Please fix Flutter doctor issues first."
            exit 1
        fi
    fi
}

# Clean and get dependencies
setup_dependencies() {
    print_status "Setting up Flutter dependencies..."
    
    # Clean previous builds
    flutter clean
    
    # Get dependencies
    flutter pub get
    
    # Generate code (for json_serializable, etc.)
    print_status "Generating code..."
    flutter packages pub run build_runner build --delete-conflicting-outputs
    
    print_success "Dependencies setup complete"
}

# Setup iOS
setup_ios() {
    print_status "Setting up iOS project..."
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # Check if Xcode is installed
        if ! command -v xcodebuild &> /dev/null; then
            print_warning "Xcode is not installed. iOS development will not be available."
            return
        fi
        
        # Check if CocoaPods is installed
        if ! command -v pod &> /dev/null; then
            print_status "Installing CocoaPods..."
            sudo gem install cocoapods
        fi
        
        # Install iOS pods
        cd ios
        pod install --repo-update
        cd ..
        
        print_success "iOS setup complete"
    else
        print_warning "iOS setup skipped (not on macOS)"
    fi
}

# Setup Android
setup_android() {
    print_status "Setting up Android project..."
    
    # Check if Android SDK is available
    if flutter doctor | grep -q "Android toolchain"; then
        print_status "Android toolchain is available"
        
        # Accept Android licenses
        flutter doctor --android-licenses
        
        print_success "Android setup complete"
    else
        print_warning "Android toolchain not found. Please install Android Studio and SDK."
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p assets/images
    mkdir -p assets/videos
    mkdir -p assets/fonts
    mkdir -p assets/models
    mkdir -p assets/icons
    
    print_success "Directories created"
}

# Setup development tools
setup_dev_tools() {
    print_status "Setting up development tools..."
    
    # Install useful Flutter packages globally
    flutter pub global activate flutter_gen
    flutter pub global activate dart_code_metrics
    
    print_success "Development tools setup complete"
}

# Verify setup
verify_setup() {
    print_status "Verifying setup..."
    
    # Check if project can be analyzed
    flutter analyze
    
    # Check if tests can run
    print_status "Running tests..."
    flutter test
    
    print_success "Setup verification complete"
}

# Create launch configurations for VS Code
create_vscode_config() {
    print_status "Creating VS Code configuration..."
    
    mkdir -p .vscode
    
    cat > .vscode/launch.json << EOF
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug (iOS)",
            "request": "launch",
            "type": "dart",
            "deviceId": "ios",
            "program": "lib/main.dart",
            "args": ["--flavor", "development"]
        },
        {
            "name": "Debug (Android)",
            "request": "launch",
            "type": "dart",
            "deviceId": "android",
            "program": "lib/main.dart",
            "args": ["--flavor", "development"]
        },
        {
            "name": "Profile",
            "request": "launch",
            "type": "dart",
            "flutterMode": "profile",
            "program": "lib/main.dart"
        },
        {
            "name": "Release",
            "request": "launch",
            "type": "dart",
            "flutterMode": "release",
            "program": "lib/main.dart"
        }
    ]
}
EOF

    cat > .vscode/settings.json << EOF
{
    "dart.flutterSdkPath": "",
    "dart.lineLength": 100,
    "editor.rulers": [100],
    "editor.formatOnSave": true,
    "dart.previewFlutterUiGuides": true,
    "dart.previewFlutterUiGuidesCustomTracking": true,
    "files.associations": {
        "*.dart": "dart"
    }
}
EOF

    print_success "VS Code configuration created"
}

# Main setup function
main() {
    echo ""
    print_status "Starting Flutter project setup..."
    echo ""
    
    # Check prerequisites
    check_flutter
    check_flutter_doctor
    
    # Setup project
    create_directories
    setup_dependencies
    setup_ios
    setup_android
    setup_dev_tools
    create_vscode_config
    
    # Verify everything works
    verify_setup
    
    echo ""
    print_success "🎉 Flutter project setup complete!"
    echo ""
    print_status "Next steps:"
    echo "  1. Open the project in your IDE (VS Code, Android Studio, etc.)"
    echo "  2. Connect a device or start an emulator"
    echo "  3. Run: flutter run"
    echo ""
    print_status "For iOS development:"
    echo "  - Make sure you have a valid Apple Developer account"
    echo "  - Update the bundle identifier in ios/Runner.xcodeproj"
    echo "  - Configure code signing in Xcode"
    echo ""
    print_status "For Android development:"
    echo "  - Update the application ID in android/app/build.gradle"
    echo "  - Configure app signing for release builds"
    echo ""
    print_status "Happy coding! 🚀"
}

# Run main function
main "$@"
