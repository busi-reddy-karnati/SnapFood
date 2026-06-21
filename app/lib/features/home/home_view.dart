import 'package:flutter/material.dart';

import '../grocery/grocery_view.dart';
import '../history/history_view.dart';
import '../intake/intake_view.dart';
import '../pantry/pantry_view.dart';
import '../settings/settings_view.dart';
import '../suggestions/suggestions_view.dart';

/// Bottom-nav shell hosting the main tabs. Settings is reachable from the
/// app-bar action.
class HomeView extends StatefulWidget {
  const HomeView({super.key});

  @override
  State<HomeView> createState() => _HomeViewState();
}

class _HomeViewState extends State<HomeView> {
  int _index = 0;

  static const _titles = ['Capture', 'Pantry', 'Grocery', 'Suggestions', 'History'];
  final _pages = const [
    IntakeView(),
    PantryView(),
    GroceryView(),
    SuggestionsView(),
    HistoryView(),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(_titles[_index]),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => Scaffold(
                  appBar: AppBar(title: const Text('Settings')),
                  body: const SettingsView(),
                ),
              ),
            ),
          ),
        ],
      ),
      body: IndexedStack(index: _index, children: _pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.add_circle_outline), label: 'Capture'),
          NavigationDestination(icon: Icon(Icons.kitchen), label: 'Pantry'),
          NavigationDestination(icon: Icon(Icons.shopping_cart), label: 'Grocery'),
          NavigationDestination(icon: Icon(Icons.auto_awesome), label: 'Ideas'),
          NavigationDestination(icon: Icon(Icons.history), label: 'History'),
        ],
      ),
    );
  }
}
