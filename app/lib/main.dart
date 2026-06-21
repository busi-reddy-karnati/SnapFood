import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'features/app_state.dart';
import 'features/home/home_view.dart';
import 'features/onboarding/onboarding_view.dart';

void main() {
  runApp(const SnapFoodApp());
}

class SnapFoodApp extends StatelessWidget {
  const SnapFoodApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AppState()..bootstrap(),
      child: MaterialApp(
        title: 'SnapFood',
        debugShowCheckedModeBanner: false,
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
          useMaterial3: true,
        ),
        home: const _Root(),
      ),
    );
  }
}

class _Root extends StatelessWidget {
  const _Root();

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();
    if (app.loading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }
    return app.onboarded ? const HomeView() : const OnboardingView();
  }
}
