/// A user-presentable error carrying the backend's `detail` message when present.
class NetworkError implements Exception {
  NetworkError(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}
