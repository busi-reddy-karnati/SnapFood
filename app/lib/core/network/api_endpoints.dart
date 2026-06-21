/// Centralised API URLs. Base URL is injected at build time via
/// `--dart-define=API_BASE_URL=...` (CI sets the prod backend); defaults to
/// localhost for local development. Mirrors Fitnesswispr's APIEndpoints.
class ApiEndpoints {
  static const String baseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://localhost:8000',
  );

  static String get _api => '$baseUrl/api/v1';

  static Uri get health => Uri.parse('$_api/health');
  static Uri get household => Uri.parse('$_api/household');
  static Uri get members => Uri.parse('$_api/household/members');
  static Uri member(String id) => Uri.parse('$_api/household/members/$id');
  static Uri get goal => Uri.parse('$_api/household/goal');
  static Uri get schedule => Uri.parse('$_api/household/schedule');

  static Uri get pantry => Uri.parse('$_api/pantry');
  static Uri pantryItem(String id) => Uri.parse('$_api/pantry/$id');

  static Uri get grocery => Uri.parse('$_api/grocery');
  static Uri groceryItem(String id) => Uri.parse('$_api/grocery/$id');

  static Uri get intake => Uri.parse('$_api/intake');
  static Uri get suggestions => Uri.parse('$_api/suggestions');
  static Uri get feedback => Uri.parse('$_api/feedback');
  static Uri get history => Uri.parse('$_api/history');
}
