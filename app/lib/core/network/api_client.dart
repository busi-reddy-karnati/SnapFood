import 'dart:convert';

import 'package:http/http.dart' as http;

import '../persistence/device_uuid.dart';
import 'network_error.dart';

/// Single HTTP client for the backend. Attaches the X-Device-UUID header on
/// every request and surfaces the backend's `detail` message on errors.
/// Mirrors Fitnesswispr's APIClient.
class ApiClient {
  ApiClient._();
  static final ApiClient shared = ApiClient._();

  final _http = http.Client();

  Future<Map<String, String>> _headers() async {
    final uuid = await DeviceUUID.shared.id;
    return {
      'Content-Type': 'application/json',
      'X-Device-UUID': uuid,
    };
  }

  Future<dynamic> get(Uri url) async {
    final resp = await _http.get(url, headers: await _headers());
    return _decode(resp);
  }

  Future<dynamic> post(Uri url, [Object? body]) async {
    final resp = await _http.post(
      url,
      headers: await _headers(),
      body: jsonEncode(body ?? {}),
    );
    return _decode(resp);
  }

  Future<dynamic> put(Uri url, [Object? body]) async {
    final resp = await _http.put(
      url,
      headers: await _headers(),
      body: jsonEncode(body ?? {}),
    );
    return _decode(resp);
  }

  Future<void> delete(Uri url) async {
    final resp = await _http.delete(url, headers: await _headers());
    if (resp.statusCode >= 400) _throw(resp);
  }

  dynamic _decode(http.Response resp) {
    if (resp.statusCode >= 400) _throw(resp);
    if (resp.body.isEmpty) return null;
    return jsonDecode(resp.body);
  }

  Never _throw(http.Response resp) {
    String message = 'Something went wrong. Please try again.';
    try {
      final decoded = jsonDecode(resp.body);
      if (decoded is Map && decoded['detail'] is String) {
        message = decoded['detail'] as String;
      }
    } catch (_) {/* keep default */}
    throw NetworkError(message, statusCode: resp.statusCode);
  }
}
