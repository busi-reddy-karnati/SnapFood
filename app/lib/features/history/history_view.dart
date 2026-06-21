import 'package:flutter/material.dart';

import '../../components/ui.dart';
import '../../core/models/suggestion.dart';
import '../../core/services/api_service.dart';

class HistoryView extends StatefulWidget {
  const HistoryView({super.key});

  @override
  State<HistoryView> createState() => _HistoryViewState();
}

class _HistoryViewState extends State<HistoryView> {
  final _api = ApiService.shared;
  late Future<List<Suggestion>> _future;

  @override
  void initState() {
    super.initState();
    _future = _api.getHistory();
  }

  String _fmt(DateTime? d) =>
      d == null ? '' : '${d.year}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: () async => setState(() => _future = _api.getHistory()),
      child: FutureBuilder<List<Suggestion>>(
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
              EmptyState(icon: Icons.history, message: 'No suggestions yet.'),
            ]);
          }
          return ListView.builder(
            itemCount: items.length,
            itemBuilder: (context, i) {
              final s = items[i];
              final groceryCount = s.grocery.length;
              final recipeCount = s.recipes.length;
              return ListTile(
                leading: const Icon(Icons.receipt_long),
                title: Text(s.kind.replaceAll('_', ' ')),
                subtitle: Text('$groceryCount groceries · $recipeCount recipes · ${_fmt(s.createdAt)}'),
              );
            },
          );
        },
      ),
    );
  }
}
