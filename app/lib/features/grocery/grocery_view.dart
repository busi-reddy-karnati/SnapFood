import 'package:flutter/material.dart';

import '../../components/ui.dart';
import '../../core/models/grocery_item.dart';
import '../../core/services/api_service.dart';

class GroceryView extends StatefulWidget {
  const GroceryView({super.key});

  @override
  State<GroceryView> createState() => _GroceryViewState();
}

class _GroceryViewState extends State<GroceryView> {
  final _api = ApiService.shared;
  late Future<List<GroceryItem>> _future;

  @override
  void initState() {
    super.initState();
    _future = _api.getGrocery();
  }

  void _reload() => setState(() => _future = _api.getGrocery());

  Future<void> _add() async {
    final controller = TextEditingController();
    final name = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add to grocery list'),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: const InputDecoration(hintText: 'Item name'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
          FilledButton(
            onPressed: () => Navigator.pop(context, controller.text.trim()),
            child: const Text('Add'),
          ),
        ],
      ),
    );
    if (name == null || name.isEmpty) return;
    try {
      await _api.addGroceryItem(name);
      _reload();
    } catch (e) {
      if (mounted) showError(context, e);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      floatingActionButton: FloatingActionButton(onPressed: _add, child: const Icon(Icons.add)),
      body: RefreshIndicator(
        onRefresh: () async => _reload(),
        child: FutureBuilder<List<GroceryItem>>(
          future: _future,
          builder: (context, snap) {
            if (snap.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snap.hasError) {
              return EmptyState(icon: Icons.error_outline, message: snap.error.toString());
            }
            final items = snap.data ?? [];
            if (items.isEmpty) {
              return ListView(children: const [
                SizedBox(height: 120),
                EmptyState(icon: Icons.shopping_cart, message: 'Your grocery list is empty.'),
              ]);
            }
            return ListView.builder(
              itemCount: items.length,
              itemBuilder: (context, i) {
                final item = items[i];
                return Dismissible(
                  key: ValueKey(item.itemId),
                  direction: DismissDirection.endToStart,
                  background: Container(
                    color: Colors.red,
                    alignment: Alignment.centerRight,
                    padding: const EdgeInsets.only(right: 20),
                    child: const Icon(Icons.delete, color: Colors.white),
                  ),
                  onDismissed: (_) async {
                    try {
                      await _api.removeGroceryItem(item.itemId);
                    } catch (e) {
                      if (mounted) showError(context, e);
                    }
                  },
                  child: ListTile(
                    leading: Icon(
                      item.source == 'suggested' ? Icons.auto_awesome : Icons.edit,
                      size: 18,
                      color: Colors.grey,
                    ),
                    title: Text(item.name),
                    subtitle: item.category != null ? Text(item.category!) : null,
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }
}
