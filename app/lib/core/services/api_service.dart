import '../models/grocery_item.dart';
import '../models/household.dart';
import '../models/pantry_item.dart';
import '../models/suggestion.dart';
import '../network/api_client.dart';
import '../network/api_endpoints.dart';

/// Typed wrapper over the REST API used by the view models.
class ApiService {
  ApiService._();
  static final ApiService shared = ApiService._();

  final _api = ApiClient.shared;

  // --- Household / goal / schedule / members --------------------------- #
  Future<Household> getHousehold() async =>
      Household.fromJson(await _api.get(ApiEndpoints.household));

  Future<Household> updateHousehold({
    String? name,
    Map<String, dynamic>? dietaryPreferences,
    List<dynamic>? cuisines,
  }) async {
    final body = <String, dynamic>{};
    if (name != null) body['name'] = name;
    if (dietaryPreferences != null) {
      body['dietary_preferences'] = dietaryPreferences;
    }
    if (cuisines != null) body['cuisines'] = cuisines;
    return Household.fromJson(await _api.put(ApiEndpoints.household, body));
  }

  Future<Household> addMember(String name, {int? age, String? notes}) async =>
      Household.fromJson(await _api.post(ApiEndpoints.members, {
        'name': name,
        if (age != null) 'age': age,
        if (notes != null) 'notes': notes,
      }));

  Future<Household> deleteMember(String memberId) async {
    await _api.delete(ApiEndpoints.member(memberId));
    return getHousehold();
  }

  Future<void> setGoal(String description, {Map<String, dynamic>? target}) =>
      _api.put(ApiEndpoints.goal,
          {'description': description, 'target': target ?? {}});

  Future<void> setSchedule(List<dynamic> meals) =>
      _api.put(ApiEndpoints.schedule, {'meals': meals});

  // --- Pantry ---------------------------------------------------------- #
  Future<List<PantryItem>> getPantry() async {
    final list = await _api.get(ApiEndpoints.pantry) as List;
    return list.map((e) => PantryItem.fromJson((e as Map).cast())).toList();
  }

  Future<PantryItem> addPantryItem(String name,
      {String? category,
      double? quantity,
      String? unit,
      String status = 'ok'}) async {
    return PantryItem.fromJson(await _api.post(ApiEndpoints.pantry, {
      'name': name,
      if (category != null) 'category': category,
      if (quantity != null) 'quantity': quantity,
      if (unit != null) 'unit': unit,
      'status': status,
    }));
  }

  Future<PantryItem> updatePantryStatus(String itemId, String status) async =>
      PantryItem.fromJson(
          await _api.put(ApiEndpoints.pantryItem(itemId), {'status': status}));

  Future<void> deletePantryItem(String itemId) =>
      _api.delete(ApiEndpoints.pantryItem(itemId));

  // --- Grocery --------------------------------------------------------- #
  Future<List<GroceryItem>> getGrocery() async {
    final list = await _api.get(ApiEndpoints.grocery) as List;
    return list.map((e) => GroceryItem.fromJson((e as Map).cast())).toList();
  }

  Future<GroceryItem> addGroceryItem(String name,
      {String? category, double? quantity, String? unit}) async {
    return GroceryItem.fromJson(await _api.post(ApiEndpoints.grocery, {
      'name': name,
      if (category != null) 'category': category,
      if (quantity != null) 'quantity': quantity,
      if (unit != null) 'unit': unit,
    }));
  }

  Future<void> removeGroceryItem(String itemId) =>
      _api.delete(ApiEndpoints.groceryItem(itemId));

  // --- Intake / suggestions / feedback / history ----------------------- #
  Future<IntakeResult> intake(
      {String? text, String? imageBase64, String? imageMime}) async {
    return IntakeResult.fromJson(await _api.post(ApiEndpoints.intake, {
      if (text != null) 'text': text,
      if (imageBase64 != null) 'image_base64': imageBase64,
      if (imageMime != null) 'image_mime': imageMime,
    }));
  }

  Future<Suggestion> generateSuggestions(List<String> kinds) async =>
      Suggestion.fromJson(
          await _api.post(ApiEndpoints.suggestions, {'kinds': kinds}));

  Future<List<Suggestion>> listSuggestions() async {
    final list = await _api.get(ApiEndpoints.suggestions) as List;
    return list.map((e) => Suggestion.fromJson((e as Map).cast())).toList();
  }

  Future<void> sendFeedback(String suggestionId, String rating,
          {String? comment}) =>
      _api.post(ApiEndpoints.feedback, {
        'suggestion_id': suggestionId,
        'rating': rating,
        if (comment != null) 'comment': comment,
      });

  Future<List<Suggestion>> getHistory() async {
    final data = await _api.get(ApiEndpoints.history) as Map;
    final list = (data['suggestions'] as List?) ?? [];
    return list.map((e) => Suggestion.fromJson((e as Map).cast())).toList();
  }
}
