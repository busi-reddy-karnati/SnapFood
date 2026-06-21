import 'package:flutter/material.dart';

import '../../components/ui.dart';
import '../../core/input/image_service.dart';
import '../../core/input/speech_service.dart';
import '../../core/models/suggestion.dart';
import '../../core/services/api_service.dart';

/// The universal capture screen: type, speak, or photograph. Sends to /intake
/// and shows what changed (pantry/grocery updates, logged preferences).
class IntakeView extends StatefulWidget {
  const IntakeView({super.key});

  @override
  State<IntakeView> createState() => _IntakeViewState();
}

class _IntakeViewState extends State<IntakeView> {
  final _api = ApiService.shared;
  final _speech = SpeechService();
  final _images = ImageService();
  final _controller = TextEditingController();

  bool _listening = false;
  bool _sending = false;
  IntakeResult? _result;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _toggleMic() async {
    if (_listening) {
      await _speech.stop();
      setState(() => _listening = false);
      return;
    }
    final ok = await _speech.init();
    if (!ok) {
      if (mounted) showError(context, 'Microphone/speech not available.');
      return;
    }
    setState(() => _listening = true);
    await _speech.start((text) => setState(() => _controller.text = text));
  }

  Future<void> _send({String? imageBase64, String? imageMime}) async {
    final text = _controller.text.trim();
    if (text.isEmpty && imageBase64 == null) {
      showError(context, 'Type, speak, or add a photo first.');
      return;
    }
    setState(() {
      _sending = true;
      _result = null;
    });
    try {
      final result = await _api.intake(
        text: text.isEmpty ? null : text,
        imageBase64: imageBase64,
        imageMime: imageMime,
      );
      if (!mounted) return;
      setState(() {
        _result = result;
        _controller.clear();
      });
    } catch (e) {
      if (mounted) showError(context, e);
    } finally {
      if (mounted) setState(() => _sending = false);
    }
  }

  Future<void> _photo({required bool fromCamera}) async {
    try {
      final img = await _images.capture(fromCamera: fromCamera);
      if (img == null) return;
      await _send(imageBase64: img.base64, imageMime: img.mime);
    } catch (e) {
      if (mounted) showError(context, e);
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text('What do you need?', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600)),
        const SizedBox(height: 4),
        const Text('e.g. "Rice is almost over, order it next time" or "I want lamb next week".',
            style: TextStyle(color: Colors.grey)),
        const SizedBox(height: 16),
        TextField(
          controller: _controller,
          minLines: 3,
          maxLines: 6,
          decoration: const InputDecoration(
            border: OutlineInputBorder(),
            hintText: 'Type here, or tap the mic to speak…',
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            IconButton.filledTonal(
              onPressed: _toggleMic,
              icon: Icon(_listening ? Icons.stop : Icons.mic),
              tooltip: _listening ? 'Stop' : 'Speak',
            ),
            IconButton.filledTonal(
              onPressed: _sending ? null : () => _photo(fromCamera: true),
              icon: const Icon(Icons.camera_alt),
              tooltip: 'Camera',
            ),
            IconButton.filledTonal(
              onPressed: _sending ? null : () => _photo(fromCamera: false),
              icon: const Icon(Icons.photo_library),
              tooltip: 'Gallery',
            ),
            const Spacer(),
            FilledButton.icon(
              onPressed: _sending ? null : () => _send(),
              icon: _sending
                  ? const SizedBox(
                      height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                  : const Icon(Icons.send),
              label: const Text('Send'),
            ),
          ],
        ),
        if (_result != null) ...[
          const SizedBox(height: 24),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(_result!.message, style: const TextStyle(fontWeight: FontWeight.w600)),
                  if (_result!.applied.isEmpty)
                    const Padding(
                      padding: EdgeInsets.only(top: 8),
                      child: Text('Noted for your next plan.', style: TextStyle(color: Colors.grey)),
                    )
                  else
                    ..._result!.applied.map((a) => Padding(
                          padding: const EdgeInsets.only(top: 8),
                          child: Row(children: [
                            const Icon(Icons.check_circle, size: 18, color: Colors.green),
                            const SizedBox(width: 8),
                            Expanded(child: Text(a)),
                          ]),
                        )),
                ],
              ),
            ),
          ),
        ],
      ],
    );
  }
}
