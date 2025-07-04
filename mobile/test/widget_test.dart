import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:snownavi_mobile/main.dart';
import 'package:snownavi_mobile/core/app_config.dart';

void main() {
  group('SnowNavi Mobile App Tests', () {
    setUpAll(() async {
      // Initialize app configuration for testing
      TestWidgetsFlutterBinding.ensureInitialized();
      await AppConfig.initialize();
    });

    testWidgets('App should start and show splash screen', (WidgetTester tester) async {
      // Build our app and trigger a frame
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      // Verify that splash screen is shown
      expect(find.text('SnowNavi'), findsOneWidget);
      expect(find.text('Pose Analyzer'), findsOneWidget);

      // Wait for splash screen animation
      await tester.pump(const Duration(seconds: 1));
    });

    testWidgets('Navigation should work correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      // Wait for app to initialize
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Should show home screen after splash
      expect(find.text('SnowNavi Pose Analyzer'), findsOneWidget);

      // Test bottom navigation
      expect(find.byIcon(Icons.home), findsOneWidget);
      expect(find.byIcon(Icons.analytics), findsOneWidget);
      expect(find.byIcon(Icons.camera_alt), findsOneWidget);
      expect(find.byIcon(Icons.settings), findsOneWidget);
    });

    testWidgets('Settings screen should be accessible', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Tap on settings tab
      await tester.tap(find.byIcon(Icons.settings));
      await tester.pumpAndSettle();

      // Verify settings screen is shown
      expect(find.text('Settings'), findsOneWidget);
      expect(find.text('Language'), findsOneWidget);
      expect(find.text('Theme'), findsOneWidget);
    });

    testWidgets('Language switching should work', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Navigate to settings
      await tester.tap(find.byIcon(Icons.settings));
      await tester.pumpAndSettle();

      // Tap on language setting
      await tester.tap(find.text('Language'));
      await tester.pumpAndSettle();

      // Should show language selection dialog
      expect(find.text('Select Language'), findsOneWidget);
      expect(find.text('English'), findsOneWidget);
      expect(find.text('中文'), findsOneWidget);
    });

    testWidgets('Theme switching should work', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Navigate to settings
      await tester.tap(find.byIcon(Icons.settings));
      await tester.pumpAndSettle();

      // Tap on theme setting
      await tester.tap(find.text('Theme'));
      await tester.pumpAndSettle();

      // Should show theme selection dialog
      expect(find.text('Theme'), findsOneWidget);
    });

    testWidgets('Video player widget should handle empty state', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Should show empty video state
      expect(find.byIcon(Icons.video_library_outlined), findsOneWidget);
      expect(find.text('No video selected'), findsOneWidget);
    });

    testWidgets('Analysis screen should be accessible', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Tap on analysis tab
      await tester.tap(find.byIcon(Icons.analytics));
      await tester.pumpAndSettle();

      // Verify analysis screen is shown
      expect(find.text('Analysis'), findsOneWidget);
    });

    testWidgets('Camera screen should be accessible', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Tap on camera tab
      await tester.tap(find.byIcon(Icons.camera_alt));
      await tester.pumpAndSettle();

      // Camera screen should handle permission requirements gracefully
      // In test environment, camera won't be available
      expect(find.text('Camera'), findsOneWidget);
    });

    testWidgets('FAB should show video source options', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Should be on home tab with FAB visible
      expect(find.byType(FloatingActionButton), findsOneWidget);

      // Tap FAB
      await tester.tap(find.byType(FloatingActionButton));
      await tester.pumpAndSettle();

      // Should show video source selection
      expect(find.text('Select Video Source'), findsOneWidget);
      expect(find.text('Record'), findsOneWidget);
      expect(find.text('Gallery'), findsOneWidget);
      expect(find.text('Files'), findsOneWidget);
    });

    testWidgets('Control panel should be visible on home screen', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Control panel should be visible
      expect(find.byType(Slider), findsOneWidget); // Pose detection sensitivity slider
      expect(find.byType(Switch), findsOneWidget); // Real-time analysis switch
    });
  });

  group('Service Tests', () {
    testWidgets('App configuration should be initialized', (WidgetTester tester) async {
      // App config should be available
      expect(AppConfig.appName, isNotEmpty);
      expect(AppConfig.version, isNotEmpty);
      expect(AppConfig.isDebug, isA<bool>());
    });

    testWidgets('Default settings should be correct', (WidgetTester tester) async {
      // Check default settings
      expect(AppConfig.language, equals('en'));
      expect(AppConfig.themeMode, equals('system'));
      expect(AppConfig.videoQuality, equals('high'));
      expect(AppConfig.poseDetectionSensitivity, equals(0.5));
    });
  });

  group('Error Handling Tests', () {
    testWidgets('App should handle initialization errors gracefully', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      // App should not crash during initialization
      await tester.pumpAndSettle(const Duration(seconds: 5));
      
      // Should eventually show some content
      expect(find.byType(Scaffold), findsWidgets);
    });
  });

  group('Accessibility Tests', () {
    testWidgets('App should be accessible', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Check for semantic labels
      expect(tester.getSemantics(find.byIcon(Icons.home)), isNotNull);
      expect(tester.getSemantics(find.byIcon(Icons.analytics)), isNotNull);
      expect(tester.getSemantics(find.byIcon(Icons.camera_alt)), isNotNull);
      expect(tester.getSemantics(find.byIcon(Icons.settings)), isNotNull);
    });
  });
}
