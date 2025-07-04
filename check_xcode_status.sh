#!/bin/bash

# SnowNavi - Xcode Installation Status Checker

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "🏂 SnowNavi Pose Analyzer - iOS Environment Status"
echo "=================================================="

# Check Xcode installation status
print_status "Checking Xcode installation status..."

if [ -d "/Applications/Xcode.app" ]; then
    print_success "Xcode is fully installed!"
    
    # Check Xcode version
    xcode_version=$(xcodebuild -version 2>/dev/null | head -n 1)
    if [ $? -eq 0 ]; then
        print_success "Xcode version: $xcode_version"
    else
        print_warning "Xcode is installed but may need to be launched and configured"
    fi
    
    # Check iOS Simulator
    print_status "Checking iOS Simulator availability..."
    simulators=$(xcrun simctl list devices ios 2>/dev/null | grep -E "iPhone|iPad" | head -5)
    if [ $? -eq 0 ] && [ ! -z "$simulators" ]; then
        print_success "iOS Simulators available:"
        echo "$simulators"
    else
        print_warning "iOS Simulators may not be available yet"
    fi
    
elif [ -f "/Applications/Xcode.appdownload" ]; then
    print_warning "Xcode is still downloading..."
    
    # Check download progress if possible
    download_size=$(du -h /Applications/Xcode.appdownload 2>/dev/null | cut -f1)
    if [ ! -z "$download_size" ]; then
        print_status "Current download size: $download_size"
    fi
    
    print_status "Please wait for Xcode download to complete"
    print_status "Xcode is approximately 15GB and may take some time to download"
    
else
    print_warning "Xcode is not installed"
    print_status "Please install Xcode from the App Store"
fi

echo ""
print_status "Current Flutter environment status:"

# Check Flutter
if command -v flutter &> /dev/null; then
    flutter_version=$(flutter --version | head -n 1)
    print_success "Flutter: $flutter_version"
else
    print_warning "Flutter is not installed"
fi

# Check CocoaPods
if command -v pod &> /dev/null; then
    pod_version=$(pod --version)
    print_success "CocoaPods: $pod_version"
else
    print_warning "CocoaPods is not installed"
fi

# Check available devices
print_status "Available Flutter devices:"
flutter devices 2>/dev/null || print_warning "Flutter devices not available"

echo ""
print_status "Next steps:"

if [ -d "/Applications/Xcode.app" ]; then
    echo "✅ Xcode is ready!"
    echo "🚀 You can now run: flutter run -d ios"
    echo "📱 Or start iOS Simulator and run the app"
else
    echo "⏳ Wait for Xcode installation to complete"
    echo "🔄 Run this script again to check status"
    echo "🌐 Meanwhile, you can test the app on web: flutter run -d chrome"
fi

echo ""
print_status "SnowNavi Pose Analyzer is ready for development! 🎿"
