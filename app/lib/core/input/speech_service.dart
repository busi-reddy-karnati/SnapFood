import 'package:speech_to_text/speech_to_text.dart';

/// On-device speech-to-text. Keeps transcription free and private (only the
/// resulting text is sent to the backend), mirroring Fitnesswispr's approach.
class SpeechService {
  final SpeechToText _speech = SpeechToText();
  bool _available = false;

  bool get isListening => _speech.isListening;

  Future<bool> init() async {
    _available = await _speech.initialize(
      onError: (_) {},
      onStatus: (_) {},
    );
    return _available;
  }

  Future<void> start(void Function(String transcript) onResult) async {
    if (!_available && !await init()) return;
    await _speech.listen(
      onResult: (r) => onResult(r.recognizedWords),
      listenOptions: SpeechListenOptions(partialResults: true),
    );
  }

  Future<void> stop() => _speech.stop();
}
