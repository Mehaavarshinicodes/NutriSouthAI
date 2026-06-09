import pandas as pd
from src.recommender import recommend_dishes

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
MEALS = ["breakfast", "lunch", "dinner", "snack"]


def generate_weekly_plan(
    df: pd.DataFrame,
    meal_calorie_split: dict,
    is_diabetic: bool,
    is_vegetarian: bool,
    spice_tolerance: str,
    exclude_gluten: bool,
    exclude_dairy: bool,
    goal: str
) -> dict:
    weekly_plan = {}
    # Track used dishes PER meal slot to prevent repeats across 7 days
    used_dishes = {meal: [] for meal in MEALS}

    for day in DAYS:
        weekly_plan[day] = {}
        for meal in MEALS:
            recs = recommend_dishes(
                df=df,
                meal_type=meal,
                calorie_target=meal_calorie_split[meal],
                is_diabetic=is_diabetic,
                is_vegetarian=is_vegetarian,
                spice_tolerance=spice_tolerance,
                exclude_gluten=exclude_gluten,
                exclude_dairy=exclude_dairy,
                goal=goal,
                n=1,
                exclude_dishes=used_dishes[meal]  # <-- pass used dishes
            )

            # If all dishes exhausted, reset and allow repeats
            if recs is None or recs.empty:
                used_dishes[meal] = []
                recs = recommend_dishes(
                    df=df,
                    meal_type=meal,
                    calorie_target=meal_calorie_split[meal],
                    is_diabetic=is_diabetic,
                    is_vegetarian=is_vegetarian,
                    spice_tolerance=spice_tolerance,
                    exclude_gluten=exclude_gluten,
                    exclude_dairy=exclude_dairy,
                    goal=goal,
                    n=1,
                    exclude_dishes=[]
                )

            if recs is not None and not recs.empty:
                used_dishes[meal].append(recs.iloc[0]["dish_name"])
                weekly_plan[day][meal] = recs
            else:
                weekly_plan[day][meal] = pd.DataFrame()

    return weekly_plan
