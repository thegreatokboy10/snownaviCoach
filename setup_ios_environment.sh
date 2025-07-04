#!/bin/bash

# SnowNavi Pose Analyzer - iOS Development Environment Setup
# This script sets up the complete iOS development environment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}"
}

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

print_step() {
    echo -e "${YELLOW}[STEP]${NC} $1"
}

# Check if running on macOS
check_macos() {
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "This script is for macOS only. iOS development requires macOS."
        exit 1
    fi
    print_success "Running on macOS $(sw_vers -productVersion)"
}

# Check and install Homebrew
install_homebrew() {
    print_step "Checking Homebrew installation..."
    
    if ! command -v brew &> /dev/null; then
        print_status "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
        
        print_success "Homebrew installed successfully"
    else
        print_success "Homebrew is already installed"
        brew update
    fi
}

# Install Xcode
install_xcode() {
    print_step "Checking Xcode installation..."
    
    if ! xcodebuild -version &> /dev/null; then
        print_warning "Xcode is not installed or not properly configured."
        print_status "Please install Xcode from the App Store:"
        print_status "1. Open App Store"
        print_status "2. Search for 'Xcode'"
        print_status "3. Install Xcode (this may take a while - it's ~15GB)"
        print_status "4. Launch Xcode and accept the license agreement"
        print_status "5. Install additional components when prompted"
        echo ""
        print_warning "After installing Xcode, please run this script again."
        
        # Open App Store to Xcode page
        open "macappstore://apps.apple.com/app/xcode/id497799835"
        
        read -p "Press Enter after you have installed Xcode and accepted the license..."
        
        # Verify Xcode installation
        if ! xcodebuild -version &> /dev/null; then
            print_error "Xcode is still not properly installed. Please check the installation."
            exit 1
        fi
    fi
    
    # Accept Xcode license
    print_status "Accepting Xcode license..."
    sudo xcodebuild -license accept
    
    # Install additional Xcode components
    print_status "Installing Xcode command line tools..."
    sudo xcode-select --install 2>/dev/null || true
    
    # Set Xcode path
    sudo xcode-select --switch /Applications/Xcode.app/Contents/Developer
    
    print_success "Xcode is properly configured"
    xcodebuild -version
}

# Install Flutter
install_flutter() {
    print_step "Installing Flutter..."
    
    if ! command -v flutter &> /dev/null; then
        print_status "Downloading and installing Flutter..."
        
        # Create development directory
        mkdir -p ~/development
        cd ~/development
        
        # Download Flutter
        curl -O https://storage.googleapis.com/flutter_infra_release/releases/stable/macos/flutter_macos_arm64_3.16.5-stable.zip
        unzip flutter_macos_arm64_3.16.5-stable.zip
        rm flutter_macos_arm64_3.16.5-stable.zip
        
        # Add Flutter to PATH
        echo 'export PATH="$PATH:$HOME/development/flutter/bin"' >> ~/.zprofile
        echo 'export PATH="$PATH:$HOME/development/flutter/bin"' >> ~/.zshrc
        export PATH="$PATH:$HOME/development/flutter/bin"
        
        print_success "Flutter installed successfully"
    else
        print_success "Flutter is already installed"
    fi
    
    # Verify Flutter installation
    flutter --version
}

# Install CocoaPods
install_cocoapods() {
    print_step "Installing CocoaPods..."
    
    if ! command -v pod &> /dev/null; then
        print_status "Installing CocoaPods via Homebrew..."
        brew install cocoapods
        print_success "CocoaPods installed successfully"
    else
        print_success "CocoaPods is already installed"
        pod --version
    fi
}

# Run Flutter Doctor
run_flutter_doctor() {
    print_step "Running Flutter Doctor..."
    
    flutter doctor -v
    
    print_status "If there are any issues above, please address them before proceeding."
    read -p "Press Enter to continue..."
}

# Setup iOS Simulator
setup_ios_simulator() {
    print_step "Setting up iOS Simulator..."
    
    # List available simulators
    print_status "Available iOS Simulators:"
    xcrun simctl list devices ios
    
    # Open Simulator
    print_status "Opening iOS Simulator..."
    open -a Simulator
    
    print_success "iOS Simulator is ready"
}

# Initialize Flutter project
init_flutter_project() {
    print_step "Initializing SnowNavi Flutter project..."
    
    cd /Users/yuwang/git/snownaviCoach
    
    # Check if mobile directory exists
    if [ ! -d "mobile" ]; then
        print_error "Mobile directory not found. Creating Flutter project..."
        flutter create mobile --org com.snownavi --project-name snownavi_mobile
    fi
    
    cd mobile
    
    # Get dependencies
    print_status "Getting Flutter dependencies..."
    flutter pub get
    
    # Setup iOS
    print_status "Setting up iOS project..."
    cd ios
    pod install
    cd ..
    
    print_success "Flutter project initialized"
}

# Run the app
run_app() {
    print_step "Running SnowNavi Pose Analyzer..."
    
    cd /Users/yuwang/git/snownaviCoach/mobile
    
    # Check for available devices
    print_status "Available devices:"
    flutter devices
    
    print_status "Starting the app on iOS Simulator..."
    flutter run -d ios
}

# Main setup function
main() {
    print_header "🏂 SnowNavi Pose Analyzer - iOS Setup"
    
    print_status "This script will set up your iOS development environment and run the SnowNavi app."
    print_status "The process includes:"
    print_status "1. Installing Homebrew (if needed)"
    print_status "2. Installing/configuring Xcode"
    print_status "3. Installing Flutter"
    print_status "4. Installing CocoaPods"
    print_status "5. Setting up iOS Simulator"
    print_status "6. Running the SnowNavi app"
    echo ""
    
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Setup cancelled."
        exit 0
    fi
    
    # Run setup steps
    check_macos
    install_homebrew
    install_xcode
    install_flutter
    install_cocoapods
    run_flutter_doctor
    setup_ios_simulator
    init_flutter_project
    
    print_header "🎉 Setup Complete!"
    print_success "Your iOS development environment is ready!"
    print_status "You can now run the SnowNavi app with: flutter run -d ios"
    
    echo ""
    read -p "Do you want to run the app now? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_app
    fi
}

# Run main function
main "$@"
