import pandas as pd

def recommend_dishes(
    df: pd.DataFrame,
    meal_type: str,
    calorie_target: float,
    is_diabetic: bool,
    is_vegetarian: bool,
    spice_tolerance: str,
    exclude_gluten: bool,
    exclude_dairy: bool,
    goal: str,
    n: int = 3,
    exclude_dishes: list = None
) -> pd.DataFrame:
    filtered = df[df["meal_type"] == meal_type].copy()

    if is_diabetic:
        filtered = filtered[filtered["is_diabetic_friendly"] == True]
    if is_vegetarian:
        filtered = filtered[filtered["veg_flag"] == True]
    if exclude_gluten:
        filtered = filtered[filtered["contains_gluten"] == False]
    if exclude_dairy:
        filtered = filtered[filtered["contains_dairy"] == False]

    spice_map = {"Low": ["low"], "Medium": ["low", "medium"], "High": ["low", "medium", "high"]}
    allowed_spice = spice_map.get(spice_tolerance, ["low", "medium"])
    filtered = filtered[filtered["spice_level"].isin(allowed_spice)]

    if exclude_dishes:
        filtered = filtered[~filtered["dish_name"].isin(exclude_dishes)]

    if filtered.empty:
        return pd.DataFrame()

    filtered = filtered.copy()
    filtered["calorie_diff"] = abs(filtered["calories"] - calorie_target)
    filtered["score"] = 0.0
    filtered["score"] -= filtered["calorie_diff"] / calorie_target

    if goal == "Weight Loss":
        filtered["score"] += filtered["is_weight_loss_friendly"].astype(int) * 0.3
        filtered["score"] += (filtered["fiber_g"] / 10)
        filtered["score"] -= (filtered["fat_g"] / 30)
    elif goal == "Muscle Gain":
        filtered["score"] += (filtered["protein_g"] / 30)
    else:
        filtered["score"] += (filtered["fiber_g"] / 15)

    if is_diabetic:
        gi_bonus = {"Low": 0.3, "Medium": 0.1, "High": -0.2}
        filtered["score"] += filtered["gi_category"].map(gi_bonus).fillna(0)

    filtered["score"] -= filtered["oil_heavy"].astype(int) * 0.15

    return filtered.nlargest(n, "score").reset_index(drop=True)


def build_reason(row: pd.Series, goal: str, is_diabetic: bool) -> str:
    reasons = []
    if is_diabetic and row.get("gi_category") == "Low":
        reasons.append("Low GI — safe for blood sugar")
    if row.get("fiber_g", 0) >= 3:
        reasons.append(f"High fiber ({row['fiber_g']}g)")
    if goal == "Weight Loss" and row.get("is_weight_loss_friendly"):
        reasons.append("Weight-loss friendly")
    if goal == "Muscle Gain" and row.get("protein_g", 0) >= 8:
        reasons.append(f"High protein ({row['protein_g']}g)")
    if not row.get("oil_heavy", False):
        reasons.append("Low oil")
    if not reasons:
        reasons.append("Fits calorie target")
    return " · ".join(reasons)