import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../../components/ui.dart';
import '../../core/persistence/device_uuid.dart';
import '../../core/services/api_service.dart';
import '../app_state.dart';

class SettingsView extends StatelessWidget {
  const SettingsView({super.key});

  @override
  Widget build(BuildContext context) {
    final app = context.watch<AppState>();
    final household = app.household;
    final api = ApiService.shared;

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text('Goal', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
        ListTile(
          contentPadding: EdgeInsets.zero,
          title: Text(household?.goal?.description ?? 'No goal set'),
          trailing: const Icon(Icons.edit),
          onTap: () async {
            final value = await _editText(context, 'Your goal', household?.goal?.description ?? '');
            if (value == null || value.isEmpty) return;
            try {
              await api.setGoal(value);
              if (context.mounted) await context.read<AppState>().refreshHousehold();
            } catch (e) {
              if (context.mounted) showError(context, e);
            }
          },
        ),
        const Divider(),
        const Text('Diet', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
        ListTile(
          contentPadding: EdgeInsets.zero,
          title: Text(household?.dietaryPreferences['diet']?.toString() ?? 'no preference'),
          subtitle: Text('Allergies: ${(household?.dietaryPreferences['allergies'] as List?)?.join(', ') ?? 'none'}'),
        ),
        const Divider(),
        Row(
          children: [
            const Expanded(
              child: Text('Members', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
            ),
            IconButton(
              icon: const Icon(Icons.person_add),
              onPressed: () async {
                final name = await _editText(context, 'Add member', '');
                if (name == null || name.isEmpty) return;
                try {
                  await api.addMember(name);
                  if (context.mounted) await context.read<AppState>().refreshHousehold();
                } catch (e) {
                  if (context.mounted) showError(context, e);
                }
              },
            ),
          ],
        ),
        ...?household?.members.map((m) => ListTile(
              contentPadding: EdgeInsets.zero,
              title: Text(m.name),
              subtitle: m.age != null ? Text('Age ${m.age}') : null,
              trailing: IconButton(
                icon: const Icon(Icons.delete_outline),
                onPressed: () async {
                  try {
                    await api.deleteMember(m.memberId);
                    if (context.mounted) await context.read<AppState>().refreshHousehold();
                  } catch (e) {
                    if (context.mounted) showError(context, e);
                  }
                },
              ),
            )),
        const Divider(),
        FutureBuilder<String>(
          future: DeviceUUID.shared.id,
          builder: (context, snap) => ListTile(
            contentPadding: EdgeInsets.zero,
            title: const Text('Device ID'),
            subtitle: Text(snap.data ?? '…'),
            dense: true,
          ),
        ),
      ],
    );
  }
}

Future<String?> _editText(BuildContext context, String title, String initial) {
  final controller = TextEditingController(text: initial);
  return showDialog<String>(
    context: context,
    builder: (context) => AlertDialog(
      title: Text(title),
      content: TextField(controller: controller, autofocus: true),
      actions: [
        TextButton(onPressed: () => Navigator.pop(context), child: const Text('Cancel')),
        FilledButton(
          onPressed: () => Navigator.pop(context, controller.text.trim()),
          child: const Text('Save'),
        ),
      ],
    ),
  );
}
