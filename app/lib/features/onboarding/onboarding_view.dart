import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../components/ui.dart';
import '../../core/services/api_service.dart';
import '../app_state.dart';

/// Collects the essentials: dietary preference, the single goal, and an optional
/// first household member. Schedule and more can be refined later in Settings.
class OnboardingView extends StatefulWidget {
  const OnboardingView({super.key});

  @override
  State<OnboardingView> createState() => _OnboardingViewState();
}

class _OnboardingViewState extends State<OnboardingView> {
  final _api = ApiService.shared;
  String _diet = 'no preference';
  final _allergies = TextEditingController();
  final _goal = TextEditingController(text: 'eat more protein');
  final _memberName = TextEditingController();
  bool _saving = false;

  static const _diets = [
    'no preference', 'vegetarian', 'vegan', 'pescatarian', 'halal', 'kosher',
  ];

  @override
  void dispose() {
    _allergies.dispose();
    _goal.dispose();
    _memberName.dispose();
    super.dispose();
  }

  Future<void> _finish() async {
    if (_goal.text.trim().isEmpty) {
      showError(context, 'Please enter a goal.');
      return;
    }
    setState(() => _saving = true);
    try {
      final allergies = _allergies.text
          .split(',')
          .map((s) => s.trim())
          .where((s) => s.isNotEmpty)
          .toList();
      await _api.updateHousehold(
        dietaryPreferences: {'diet': _diet, 'allergies': allergies},
      );
      await _api.setGoal(_goal.text.trim());
      if (_memberName.text.trim().isNotEmpty) {
        await _api.addMember(_memberName.text.trim());
      }
      if (!mounted) return;
      await context.read<AppState>().completeOnboarding();
    } catch (e) {
      if (mounted) showError(context, e);
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Welcome to SnapFood')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Tell us a little so we can plan meals for your household.',
              style: TextStyle(fontSize: 16)),
          const SizedBox(height: 24),
          const Text('Dietary preference'),
          DropdownButton<String>(
            value: _diet,
            isExpanded: true,
            items: _diets
                .map((d) => DropdownMenuItem(value: d, child: Text(d)))
                .toList(),
            onChanged: (v) => setState(() => _diet = v ?? 'no preference'),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _allergies,
            decoration: const InputDecoration(
              labelText: 'Allergies (comma-separated)',
              hintText: 'peanuts, shellfish',
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _goal,
            decoration: const InputDecoration(
              labelText: 'Your goal',
              hintText: 'eat more protein',
            ),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _memberName,
            decoration: const InputDecoration(
              labelText: 'Add a household member (optional)',
              hintText: 'Name',
            ),
          ),
          const SizedBox(height: 32),
          FilledButton(
            onPressed: _saving ? null : _finish,
            child: _saving
                ? const SizedBox(
                    height: 18, width: 18, child: CircularProgressIndicator(strokeWidth: 2))
                : const Text('Get started'),
          ),
        ],
      ),
    );
  }
}
