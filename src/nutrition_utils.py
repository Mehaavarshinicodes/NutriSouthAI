def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor BMR formula."""
    if gender.lower() == "male":
        return 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        return 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

ACTIVITY_MULTIPLIERS = {
    "Sedentary (little/no exercise)": 1.2,
    "Lightly Active (1-3 days/week)": 1.375,
    "Moderately Active (3-5 days/week)": 1.55,
    "Very Active (6-7 days/week)": 1.725,
}

def calculate_tdee(bmr: float, activity_level: str) -> float:
    """Total Daily Energy Expenditure."""
    return bmr * ACTIVITY_MULTIPLIERS.get(activity_level, 1.2)

def calculate_target_calories(tdee: float, goal: str) -> float:
    if goal == "Weight Loss":
        return tdee - 400
    elif goal == "Weight Gain":
        return tdee + 300
    else:
        return tdee

def get_meal_calorie_split(total_calories: float) -> dict:
    """Split daily calories across 4 meals."""
    return {
        "breakfast": round(total_calories * 0.25),
        "lunch":     round(total_calories * 0.35),
        "dinner":    round(total_calories * 0.25),
        "snack":     round(total_calories * 0.15),
    }

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)

def bmi_category(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"
