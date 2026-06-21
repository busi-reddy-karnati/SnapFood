class GroceryItem {
  GroceryItem({
    required this.itemId,
    required this.name,
    this.category,
    this.quantity,
    this.unit,
    this.source = 'manual',
    this.status = 'active',
  });

  final String itemId;
  final String name;
  final String? category;
  final double? quantity;
  final String? unit;
  final String source; // manual / suggested
  final String status; // active / removed / purchased

  factory GroceryItem.fromJson(Map<String, dynamic> j) => GroceryItem(
        itemId: j['item_id'] as String,
        name: j['name'] as String,
        category: j['category'] as String?,
        quantity: (j['quantity'] as num?)?.toDouble(),
        unit: j['unit'] as String?,
        source: j['source'] as String? ?? 'manual',
        status: j['status'] as String? ?? 'active',
      );
}
