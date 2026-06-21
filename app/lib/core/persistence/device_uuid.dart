import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:uuid/uuid.dart';

/// Per-device identity, persisted in the platform secure store (Keychain /
/// Android Keystore). v0 has no login: this UUID is the household key, mirroring
/// Fitnesswispr's DeviceUUID.
class DeviceUUID {
  DeviceUUID._();
  static final DeviceUUID shared = DeviceUUID._();

  static const _key = 'snapfood_device_uuid';
  final _storage = const FlutterSecureStorage();
  String? _cached;

  Future<String> get id async {
    if (_cached != null) return _cached!;
    var value = await _storage.read(key: _key);
    if (value == null || value.isEmpty) {
      value = const Uuid().v4();
      await _storage.write(key: _key, value: value);
    }
    _cached = value;
    return value;
  }
}
