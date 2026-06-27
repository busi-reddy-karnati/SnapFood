import 'package:flutter_test/flutter_test.dart';

import 'package:snapfood/main.dart';

void main() {
  testWidgets('SnapFoodApp smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const SnapFoodApp());
    expect(find.byType(SnapFoodApp), findsOneWidget);
  });
}
