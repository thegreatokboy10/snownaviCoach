# SnowNavi Pose Analyzer - Mobile Edition

A professional Flutter mobile application for pose analysis and sports coaching, specifically designed for skiing coaches and sports analysts.

## 🎯 Features

### Core Functionality
- **Real-time Pose Detection**: Advanced pose analysis using Google ML Kit
- **Video Analysis**: Load and analyze videos from gallery or record new ones
- **Multi-language Support**: English and Chinese (Simplified) with automatic detection
- **Cross-platform**: Optimized for both iOS and Android (iOS priority)

### Video Capabilities
- **Video Recording**: High-quality video recording with pose detection overlay
- **Video Playback**: Smooth video playback with pose visualization
- **Export Functionality**: Export analyzed videos with pose landmarks
- **Multiple Formats**: Support for MP4, AVI, MOV, and other common formats

### Pose Analysis
- **Real-time Detection**: Live pose detection during video recording
- **Confidence Scoring**: Adjustable confidence thresholds
- **Landmark Visualization**: Customizable landmark colors and sizes
- **Connection Lines**: Visual connections between body landmarks
- **Body Part Filtering**: Focus on specific body parts (face, upper body, lower body, etc.)

### User Experience
- **Modern UI**: Material Design 3 with custom SnowNavi branding
- **Dark/Light Themes**: Automatic theme switching based on system preferences
- **Responsive Design**: Optimized for various screen sizes
- **Gesture Controls**: Intuitive touch controls for video playback
- **Permission Management**: Seamless permission handling for camera and storage

## 🏗️ Architecture

### Project Structure
```
mobile/
├── lib/
│   ├── core/                     # Core functionality
│   │   ├── app_config.dart       # App configuration and settings
│   │   ├── localization/         # Multi-language support
│   │   ├── providers/            # State management (Riverpod)
│   │   ├── theme/               # App theming and colors
│   │   └── utils/               # Utility functions and logging
│   ├── models/                   # Data models
│   │   └── video_model.dart     # Video and pose detection models
│   ├── services/                 # Business logic services
│   │   ├── video_service.dart   # Video handling and playback
│   │   ├── pose_detection_service.dart # Pose detection logic
│   │   ├── camera_service.dart  # Camera functionality
│   │   └── permission_service.dart # Permission management
│   ├── presentation/             # UI layer
│   │   ├── screens/             # Main application screens
│   │   └── widgets/             # Reusable UI components
│   └── main.dart                # Application entry point
├── assets/                       # Static assets
│   ├── locales/                 # Translation files
│   ├── images/                  # App images and icons
│   └── fonts/                   # Custom fonts
├── ios/                         # iOS-specific configuration
└── android/                     # Android-specific configuration
```

### State Management
- **Riverpod**: Modern state management solution
- **Provider Pattern**: Clean separation of business logic
- **Reactive UI**: Automatic UI updates based on state changes

### Services Architecture
- **Video Service**: Handles video loading, playback, and export
- **Pose Detection Service**: Manages ML Kit pose detection
- **Camera Service**: Controls camera functionality and recording
- **Permission Service**: Manages app permissions with user-friendly dialogs

## 🚀 Getting Started

### Prerequisites
- Flutter SDK (>=3.10.0)
- Dart SDK (>=3.0.0)
- iOS development: Xcode 14+ and iOS 12+
- Android development: Android Studio and API level 21+

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mobile
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **iOS Setup**
   ```bash
   cd ios
   pod install
   cd ..
   ```

4. **Run the application**
   ```bash
   # For iOS
   flutter run -d ios
   
   # For Android
   flutter run -d android
   ```

### Configuration

#### iOS Configuration
- Update `ios/Runner/Info.plist` with your app details
- Set your development team in `ios/Podfile`
- Configure app icons in `ios/Runner/Assets.xcassets/`

#### Android Configuration
- Update `android/app/src/main/AndroidManifest.xml`
- Configure app icons in `android/app/src/main/res/`

## 📱 Platform-Specific Features

### iOS Optimizations
- **Native Performance**: Optimized for iOS hardware acceleration
- **Metal Framework**: Enhanced graphics performance
- **AVFoundation**: Native video processing
- **Privacy Compliance**: Full iOS privacy manifest support
- **App Store Ready**: Configured for App Store submission

### Android Support
- **Material Design**: Native Android design patterns
- **Camera2 API**: Advanced camera functionality
- **Scoped Storage**: Modern Android file management
- **Adaptive Icons**: Support for Android adaptive icons

## 🎨 Theming and Customization

### Color Scheme
- **Primary**: SnowNavi Blue (#2196F3)
- **Secondary**: Success Green (#4CAF50)
- **Accent**: Warning Orange (#FF9800)
- **Error**: Error Red (#F44336)

### Typography
- **Primary Font**: SF Pro Display (iOS) / Roboto (Android)
- **Secondary Font**: Roboto
- **Responsive Scaling**: Automatic text scaling prevention

### Dark Mode Support
- Automatic system theme detection
- Manual theme switching
- Consistent color schemes across themes

## 🌍 Internationalization

### Supported Languages
- **English (en_US)**: Default language
- **Chinese Simplified (zh_CN)**: Full translation support

### Adding New Languages
1. Create new translation file in `assets/locales/`
2. Add language to `AppLocalizations.supportedLocales`
3. Update language selection in settings

## 🔒 Privacy and Permissions

### Required Permissions
- **Camera**: Video recording and real-time pose detection
- **Microphone**: Audio recording with videos
- **Photo Library**: Saving and loading videos
- **Storage**: File management and data persistence

### Privacy Features
- Transparent permission requests
- User-friendly permission dialogs
- Privacy-first data handling
- No data collection without consent

## 🧪 Testing

### Running Tests
```bash
# Unit tests
flutter test

# Integration tests
flutter test integration_test/

# Widget tests
flutter test test/widget_test.dart
```

### Test Coverage
- Unit tests for services and models
- Widget tests for UI components
- Integration tests for user flows

## 📦 Building for Release

### iOS Release Build
```bash
flutter build ios --release
```

### Android Release Build
```bash
flutter build apk --release
# or
flutter build appbundle --release
```

## 🔧 Performance Optimizations

### Video Performance
- Hardware-accelerated video decoding
- Efficient memory management
- Background processing for pose detection
- Optimized frame rendering

### ML Performance
- Google ML Kit optimizations
- Confidence threshold tuning
- Efficient landmark processing
- Real-time performance monitoring

## 📈 Analytics and Monitoring

### Logging
- Comprehensive logging system
- Performance monitoring
- Error tracking and reporting
- User interaction analytics

### Debug Tools
- Development-only debug panels
- Performance profiling
- Memory usage monitoring
- Network request logging

## 🤝 Contributing

### Development Guidelines
- Follow Flutter best practices
- Maintain consistent code style
- Write comprehensive tests
- Update documentation

### Code Style
- Use `flutter analyze` for linting
- Follow Dart style guide
- Maintain consistent naming conventions
- Document public APIs

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation wiki

## 🚀 Roadmap

### Upcoming Features
- Advanced pose analysis algorithms
- Cloud synchronization
- Team collaboration features
- Enhanced export options
- Performance analytics dashboard

### Platform Expansion
- iPad optimization
- Apple Watch companion app
- Android tablet support
- Web platform support

---

**SnowNavi Pose Analyzer** - Empowering coaches with advanced pose analysis technology.
