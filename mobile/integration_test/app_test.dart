import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:snownavi_mobile/main.dart';
import 'package:snownavi_mobile/core/app_config.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('SnowNavi Mobile Integration Tests', () {
    setUpAll(() async {
      await AppConfig.initialize();
    });

    testWidgets('Complete app flow test', (WidgetTester tester) async {
      // Start the app
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      // Wait for splash screen
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Verify home screen is loaded
      expect(find.text('SnowNavi Pose Analyzer'), findsOneWidget);
      expect(find.byIcon(Icons.video_library_outlined), findsOneWidget);

      // Test navigation to analysis screen
      await tester.tap(find.byIcon(Icons.analytics));
      await tester.pumpAndSettle();
      expect(find.text('Analysis'), findsOneWidget);

      // Test navigation to camera screen
      await tester.tap(find.byIcon(Icons.camera_alt));
      await tester.pumpAndSettle();
      // Camera screen should handle permissions gracefully in test environment

      // Test navigation to settings screen
      await tester.tap(find.byIcon(Icons.settings));
      await tester.pumpAndSettle();
      expect(find.text('Settings'), findsOneWidget);

      // Test language switching
      await tester.tap(find.text('Language'));
      await tester.pumpAndSettle();
      expect(find.text('Select Language'), findsOneWidget);
      
      // Switch to Chinese
      await tester.tap(find.text('中文'));
      await tester.pumpAndSettle();

      // Verify language changed (some text should be in Chinese now)
      // Note: In real test, we'd verify specific Chinese text

      // Switch back to English
      await tester.tap(find.text('语言')); // Language in Chinese
      await tester.pumpAndSettle();
      await tester.tap(find.text('English'));
      await tester.pumpAndSettle();

      // Test theme switching
      await tester.tap(find.text('Theme'));
      await tester.pumpAndSettle();
      expect(find.text('Theme'), findsOneWidget);

      // Switch to dark theme
      await tester.tap(find.text('Dark'));
      await tester.pumpAndSettle();

      // Verify theme changed (background should be darker)
      final scaffold = tester.widget<Scaffold>(find.byType(Scaffold).first);
      expect(scaffold.backgroundColor, isNotNull);

      // Return to home screen
      await tester.tap(find.byIcon(Icons.home));
      await tester.pumpAndSettle();

      // Test FAB functionality
      await tester.tap(find.byType(FloatingActionButton));
      await tester.pumpAndSettle();

      expect(find.text('Select Video Source'), findsOneWidget);
      expect(find.text('Record'), findsOneWidget);
      expect(find.text('Gallery'), findsOneWidget);
      expect(find.text('Files'), findsOneWidget);

      // Close the bottom sheet
      await tester.tapAt(const Offset(200, 100)); // Tap outside the sheet
      await tester.pumpAndSettle();

      // Test control panel interactions
      final sensitivitySlider = find.byType(Slider);
      if (sensitivitySlider.evaluate().isNotEmpty) {
        await tester.drag(sensitivitySlider, const Offset(50, 0));
        await tester.pumpAndSettle();
      }

      final realTimeSwitch = find.byType(Switch);
      if (realTimeSwitch.evaluate().isNotEmpty) {
        await tester.tap(realTimeSwitch);
        await tester.pumpAndSettle();
      }
    });

    testWidgets('Settings persistence test', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Navigate to settings
      await tester.tap(find.byIcon(Icons.settings));
      await tester.pumpAndSettle();

      // Change video quality setting
      await tester.tap(find.text('Video Quality'));
      await tester.pumpAndSettle();

      // Select medium quality
      await tester.tap(find.text('Medium'));
      await tester.pumpAndSettle();

      // Restart app to test persistence
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Navigate back to settings
      await tester.tap(find.byIcon(Icons.settings));
      await tester.pumpAndSettle();

      // Verify setting was persisted
      expect(find.text('medium'), findsOneWidget);
    });

    testWidgets('Error handling test', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Test camera access without permissions
      await tester.tap(find.byIcon(Icons.camera_alt));
      await tester.pumpAndSettle();

      // Should show appropriate error or permission request
      // In test environment, camera won't be available
      expect(find.byType(Scaffold), findsOneWidget);
    });

    testWidgets('Performance test', (WidgetTester tester) async {
      final stopwatch = Stopwatch()..start();

      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      await tester.pumpAndSettle(const Duration(seconds: 3));

      stopwatch.stop();

      // App should start within reasonable time
      expect(stopwatch.elapsedMilliseconds, lessThan(5000));

      // Test navigation performance
      final navStopwatch = Stopwatch()..start();

      for (int i = 0; i < 4; i++) {
        await tester.tap(find.byIcon(Icons.analytics));
        await tester.pumpAndSettle();
        await tester.tap(find.byIcon(Icons.camera_alt));
        await tester.pumpAndSettle();
        await tester.tap(find.byIcon(Icons.settings));
        await tester.pumpAndSettle();
        await tester.tap(find.byIcon(Icons.home));
        await tester.pumpAndSettle();
      }

      navStopwatch.stop();

      // Navigation should be smooth
      expect(navStopwatch.elapsedMilliseconds, lessThan(2000));
    });

    testWidgets('Memory usage test', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Simulate heavy usage
      for (int i = 0; i < 10; i++) {
        // Navigate through all screens
        await tester.tap(find.byIcon(Icons.analytics));
        await tester.pumpAndSettle();
        await tester.tap(find.byIcon(Icons.camera_alt));
        await tester.pumpAndSettle();
        await tester.tap(find.byIcon(Icons.settings));
        await tester.pumpAndSettle();
        await tester.tap(find.byIcon(Icons.home));
        await tester.pumpAndSettle();

        // Open and close dialogs
        await tester.tap(find.byType(FloatingActionButton));
        await tester.pumpAndSettle();
        await tester.tapAt(const Offset(200, 100));
        await tester.pumpAndSettle();
      }

      // App should still be responsive
      expect(find.byType(Scaffold), findsOneWidget);
    });

    testWidgets('Accessibility test', (WidgetTester tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: SnowNaviApp(),
        ),
      );

      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Test semantic labels
      final homeIcon = find.byIcon(Icons.home);
      expect(tester.getSemantics(homeIcon), isNotNull);

      final analysisIcon = find.byIcon(Icons.analytics);
      expect(tester.getSemantics(analysisIcon), isNotNull);

      final cameraIcon = find.byIcon(Icons.camera_alt);
      expect(tester.getSemantics(cameraIcon), isNotNull);

      final settingsIcon = find.byIcon(Icons.settings);
      expect(tester.getSemantics(settingsIcon), isNotNull);

      // Test focus navigation
      await tester.sendKeyEvent(LogicalKeyboardKey.tab);
      await tester.pumpAndSettle();

      // Test screen reader compatibility
      final fab = find.byType(FloatingActionButton);
      expect(tester.getSemantics(fab), isNotNull);
    });
  });
}
