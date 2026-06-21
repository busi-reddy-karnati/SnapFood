import 'package:flutter/material.dart';

import '../../components/ui.dart';
import '../../core/models/pantry_item.dart';
import '../../core/services/api_service.dart';

class PantryView extends StatefulWidget {
  const PantryView({super.key});

  @override
  State<PantryView> createState() => _PantryViewState();
}

class _PantryViewState extends State<PantryView> {
  final _api = ApiService.shared;
  late Future<List<PantryItem>> _future;

  @override
  void initState() {
    super.initState();
    _future = _api.getPantry();
  }

  void _reload() => setState(() => _future = _api.getPantry());

  Future<void> _add() async {
    final name = await _promptName(context, 'Add pantry item');
    if (name == null || name.isEmpty) return;
    try {
      await _api.addPantryItem(name);
      _reload();
    } catch (e) {
      if (mounted) showError(context, e);
    }
  }

  Future<void> _cycleStatus(PantryItem item) async {
    const order = ['ok', 'low', 'out'];
    final next = order[(order.indexOf(item.status) + 1) % order.length];
    try {
      await _api.updatePantryStatus(item.itemId, next);
      _reload();
    } catch (e) {
      if (mounted) showError(context, e);
    }
  }

  Color _statusColor(String s) =>
      {'ok': Colors.green, 'low': Colors.orange, 'out': Colors.red}[s] ?? Colors.grey;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      floatingActionButton: FloatingActionButton(onPressed: _add, child: const Icon(Icons.add)),
      body: RefreshIndicator(
        onRefresh: () async => _reload(),
        child: FutureBuilder<List<PantryItem>>(
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
                EmptyState(icon: Icons.kitchen, message: 'Your pantry is empty.\nAdd items or snap a photo on the Capture tab.'),
              ]);
            }
            return ListView.builder(
              itemCount: items.length,
              itemBuilder: (context, i) {
                final item = items[i];
                return ListTile(
                  title: Text(item.name),
                  subtitle: item.category != null ? Text(item.category!) : null,
                  trailing: GestureDetector(
                    onTap: () => _cycleStatus(item),
                    child: Chip(
                      label: Text(item.status.toUpperCase()),
                      backgroundColor: _statusColor(item.status).withValues(alpha: 0.15),
                      labelStyle: TextStyle(color: _statusColor(item.status)),
                    ),
                  ),
                  onLongPress: () async {
                    try {
                      await _api.deletePantryItem(item.itemId);
                      _reload();
                    } catch (e) {
                      if (mounted) showError(context, e);
                    }
                  },
                );
              },
            );
          },
        ),
      ),
    );
  }
}

Future<String?> _promptName(BuildContext context, String title) {
  final controller = TextEditingController();
  return showDialog<String>(
    context: context,
    builder: (context) => AlertDialog(
      title: Text(title),
      content: TextField(
        controller: controller,
        autofocus: true,
        decoration: const InputDecoration(hintText: 'Name'),
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
}
