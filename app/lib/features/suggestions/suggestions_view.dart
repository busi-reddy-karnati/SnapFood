import 'package:flutter/material.dart';

import '../../components/ui.dart';
import '../../core/models/suggestion.dart';
import '../../core/services/api_service.dart';

class SuggestionsView extends StatefulWidget {
  const SuggestionsView({super.key});

  @override
  State<SuggestionsView> createState() => _SuggestionsViewState();
}

class _SuggestionsViewState extends State<SuggestionsView> {
  final _api = ApiService.shared;
  Suggestion? _current;
  bool _loading = false;

  Future<void> _generate() async {
    setState(() => _loading = true);
    try {
      final s =
          await _api.generateSuggestions(['grocery_list', 'cook_with_pantry']);
      if (mounted) setState(() => _current = s);
    } catch (e) {
      if (mounted) showError(context, e);
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _addToGrocery(Map<String, dynamic> item) async {
    try {
      await _api.addGroceryItem(
        item['name'] as String,
        category: item['category'] as String?,
        quantity: (item['quantity'] as num?)?.toDouble(),
        unit: item['unit'] as String?,
      );
      if (mounted) showInfo(context, 'Added ${item['name']} to grocery list');
    } catch (e) {
      if (mounted) showError(context, e);
    }
  }

  Future<void> _feedback(String rating) async {
    if (_current == null) return;
    try {
      await _api.sendFeedback(_current!.suggestionId, rating);
      if (mounted) {
        showInfo(context,
            rating == 'up' ? 'Glad you liked it!' : "Thanks — we'll adjust.");
      }
    } catch (e) {
      if (mounted) showError(context, e);
    }
  }

  @override
  Widget build(BuildContext context) {
    final s = _current;
    return Scaffold(
      body: s == null
          ? Center(
              child: _loading
                  ? const CircularProgressIndicator()
                  : FilledButton.icon(
                      onPressed: _generate,
                      icon: const Icon(Icons.auto_awesome),
                      label: const Text('Generate suggestions'),
                    ),
            )
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (s.rationale.isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: Text(s.rationale,
                        style: const TextStyle(fontStyle: FontStyle.italic)),
                  ),
                if (s.grocery.isNotEmpty) ...[
                  const Text('Suggested groceries',
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 8),
                  ...s.grocery.map((g) {
                    final item = (g as Map).cast<String, dynamic>();
                    final reason = item['reason'] as String?;
                    return Card(
                      child: ListTile(
                        title: Text(item['name']?.toString() ?? ''),
                        subtitle: reason != null ? Text(reason) : null,
                        trailing: IconButton(
                          icon: const Icon(Icons.add_shopping_cart),
                          onPressed: () => _addToGrocery(item),
                        ),
                      ),
                    );
                  }),
                ],
                if (s.recipes.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  const Text('Cook with what you have',
                      style:
                          TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 8),
                  ...s.recipes.map((r) {
                    final recipe = (r as Map).cast<String, dynamic>();
                    final uses =
                        (recipe['uses_pantry'] as List?)?.join(', ') ?? '';
                    final needs = (recipe['needs'] as List?)?.join(', ') ?? '';
                    return Card(
                      child: ListTile(
                        title: Text(recipe['title']?.toString() ?? 'Recipe'),
                        subtitle: Text([
                          if (uses.isNotEmpty) 'Uses: $uses',
                          if (needs.isNotEmpty) 'Needs: $needs',
                        ].join('\n')),
                        isThreeLine: uses.isNotEmpty && needs.isNotEmpty,
                      ),
                    );
                  }),
                ],
                const SizedBox(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    OutlinedButton.icon(
                      onPressed: () => _feedback('up'),
                      icon: const Icon(Icons.thumb_up),
                      label: const Text('Helpful'),
                    ),
                    OutlinedButton.icon(
                      onPressed: () => _feedback('down'),
                      icon: const Icon(Icons.thumb_down),
                      label: const Text('Not for me'),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                TextButton.icon(
                  onPressed: _loading ? null : _generate,
                  icon: const Icon(Icons.refresh),
                  label: const Text('Regenerate'),
                ),
              ],
            ),
    );
  }
}
