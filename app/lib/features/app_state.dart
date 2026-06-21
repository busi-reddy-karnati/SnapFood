import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../core/models/household.dart';
import '../core/services/api_service.dart';

/// Top-level app state: whether onboarding is done and the current household.
class AppState extends ChangeNotifier {
  static const _onboardedKey = 'snapfood_onboarded';

  bool _loading = true;
  bool _onboarded = false;
  Household? household;

  bool get loading => _loading;
  bool get onboarded => _onboarded;

  Future<void> bootstrap() async {
    final prefs = await SharedPreferences.getInstance();
    _onboarded = prefs.getBool(_onboardedKey) ?? false;
    try {
      household = await ApiService.shared.getHousehold();
      // A saved goal is a reliable signal onboarding was completed before.
      if (household?.goal != null) _onboarded = true;
    } catch (_) {/* offline / first run — stay on onboarding */}
    _loading = false;
    notifyListeners();
  }

  Future<void> refreshHousehold() async {
    household = await ApiService.shared.getHousehold();
    notifyListeners();
  }

  Future<void> completeOnboarding() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_onboardedKey, true);
    _onboarded = true;
    await refreshHousehold();
  }
}
