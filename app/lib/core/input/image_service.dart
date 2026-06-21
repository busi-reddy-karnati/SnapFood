import 'dart:convert';

import 'package:image_picker/image_picker.dart';

class CapturedImage {
  CapturedImage({required this.base64, required this.mime});
  final String base64;
  final String mime;
}

/// Capture a photo (camera) or pick one (gallery) and return it base64-encoded
/// ready for the /intake endpoint.
class ImageService {
  final ImagePicker _picker = ImagePicker();

  Future<CapturedImage?> capture({required bool fromCamera}) async {
    final XFile? file = await _picker.pickImage(
      source: fromCamera ? ImageSource.camera : ImageSource.gallery,
      maxWidth: 1280,
      imageQuality: 80,
    );
    if (file == null) return null;
    final bytes = await file.readAsBytes();
    final mime = file.mimeType ??
        (file.path.toLowerCase().endsWith('.png') ? 'image/png' : 'image/jpeg');
    return CapturedImage(base64: base64Encode(bytes), mime: mime);
  }
}
