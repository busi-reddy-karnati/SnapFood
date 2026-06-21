class PantryItem {
  PantryItem({
    required this.itemId,
    required this.name,
    this.category,
    this.quantity,
    this.unit,
    this.status = 'ok',
  });

  final String itemId;
  final String name;
  final String? category;
  final double? quantity;
  final String? unit;
  final String status; // ok / low / out

  factory PantryItem.fromJson(Map<String, dynamic> j) => PantryItem(
        itemId: j['item_id'] as String,
        name: j['name'] as String,
        category: j['category'] as String?,
        quantity: (j['quantity'] as num?)?.toDouble(),
        unit: j['unit'] as String?,
        status: j['status'] as String? ?? 'ok',
      );
}
