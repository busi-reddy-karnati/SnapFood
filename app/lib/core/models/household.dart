class Member {
  Member({
    required this.memberId,
    required this.name,
    this.age,
    this.dietaryPreferences = const {},
    this.notes,
  });

  final String memberId;
  final String name;
  final int? age;
  final Map<String, dynamic> dietaryPreferences;
  final String? notes;

  factory Member.fromJson(Map<String, dynamic> j) => Member(
        memberId: j['member_id'] as String,
        name: j['name'] as String,
        age: j['age'] as int?,
        dietaryPreferences:
            (j['dietary_preferences'] as Map?)?.cast<String, dynamic>() ?? {},
        notes: j['notes'] as String?,
      );
}

class Goal {
  Goal(
      {required this.goalId,
      required this.description,
      this.target = const {}});

  final String goalId;
  final String description;
  final Map<String, dynamic> target;

  factory Goal.fromJson(Map<String, dynamic> j) => Goal(
        goalId: j['goal_id'] as String,
        description: j['description'] as String,
        target: (j['target'] as Map?)?.cast<String, dynamic>() ?? {},
      );
}

class Schedule {
  Schedule({required this.scheduleId, this.meals = const []});

  final String scheduleId;
  final List<dynamic> meals;

  factory Schedule.fromJson(Map<String, dynamic> j) => Schedule(
        scheduleId: j['schedule_id'] as String,
        meals: (j['meals'] as List?) ?? [],
      );
}

class Household {
  Household({
    required this.householdId,
    this.name,
    this.dietaryPreferences = const {},
    this.cuisines = const [],
    this.goal,
    this.schedule,
    this.members = const [],
  });

  final String householdId;
  final String? name;
  final Map<String, dynamic> dietaryPreferences;
  final List<dynamic> cuisines;
  final Goal? goal;
  final Schedule? schedule;
  final List<Member> members;

  factory Household.fromJson(Map<String, dynamic> j) => Household(
        householdId: j['household_id'] as String,
        name: j['name'] as String?,
        dietaryPreferences:
            (j['dietary_preferences'] as Map?)?.cast<String, dynamic>() ?? {},
        cuisines: (j['cuisines'] as List?) ?? [],
        goal: j['goal'] == null
            ? null
            : Goal.fromJson((j['goal'] as Map).cast<String, dynamic>()),
        schedule: j['schedule'] == null
            ? null
            : Schedule.fromJson((j['schedule'] as Map).cast<String, dynamic>()),
        members: ((j['members'] as List?) ?? [])
            .map((m) => Member.fromJson((m as Map).cast<String, dynamic>()))
            .toList(),
      );
}
