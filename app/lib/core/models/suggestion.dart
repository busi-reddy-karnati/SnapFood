class Suggestion {
  Suggestion({
    required this.suggestionId,
    required this.kind,
    this.payload = const {},
    this.createdAt,
  });

  final String suggestionId;
  final String kind; // grocery_list / cook_with_pantry / recipe
  final Map<String, dynamic> payload;
  final DateTime? createdAt;

  List<dynamic> get grocery => (payload['grocery'] as List?) ?? const [];
  List<dynamic> get recipes => (payload['recipes'] as List?) ?? const [];
  String get rationale => payload['rationale'] as String? ?? '';

  factory Suggestion.fromJson(Map<String, dynamic> j) => Suggestion(
        suggestionId: j['suggestion_id'] as String,
        kind: j['kind'] as String,
        payload: (j['payload'] as Map?)?.cast<String, dynamic>() ?? {},
        createdAt: j['created_at'] == null
            ? null
            : DateTime.tryParse(j['created_at'] as String),
      );
}

class IntakeResult {
  IntakeResult(
      {required this.message, this.applied = const [], this.intentType});

  final String message;
  final List<String> applied;
  final String? intentType;

  factory IntakeResult.fromJson(Map<String, dynamic> j) => IntakeResult(
        message: j['message'] as String? ?? 'Got it.',
        applied:
            ((j['applied'] as List?) ?? []).map((e) => e.toString()).toList(),
        intentType: j['intent_type'] as String?,
      );
}
