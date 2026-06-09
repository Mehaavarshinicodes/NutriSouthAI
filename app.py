import streamlit as st
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")
import sys, os
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))

from config import GROK_API_KEY
from auth import require_login, logout, save_profile, get_profile
from src.data_loader import load_dishes
from src.nutrition_utils import (
    calculate_bmr, calculate_tdee, calculate_target_calories,
    get_meal_calorie_split, calculate_bmi, bmi_category
)
from src.recommender import recommend_dishes, build_reason
from src.chatbot import render_floating_chatbot
from src.weekly_planner import generate_weekly_plan
from src.festival_planner import get_festival_plan, list_festivals

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NutriSouth AI",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Auth ───────────────────────────────────────────────────────────────────────
require_login()

# ── Global styles ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main-title {
    font-size: 1.8rem;
    font-weight: 700;
    color: #1a6b3c;
    margin-bottom: 0.2rem;
}
.page-subtitle {
    color: #6b7280;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}
.meal-card {
    background: #ffffff;
    border: 1px solid #e5f0e5;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s;
}
.meal-card:hover { box-shadow: 0 4px 12px rgba(26,107,60,0.12); }
.dish-name { font-size: 1rem; font-weight: 600; color: #1a6b3c; }
.section-header {
    color: #1a6b3c;
    font-size: 1.1rem;
    font-weight: 600;
    padding-bottom: 6px;
    border-bottom: 2px solid #d0ead0;
    margin-bottom: 0.8rem;
}
.gi-low  { color: #16a34a; font-weight: 600; }
.gi-medium { color: #d97706; font-weight: 600; }
.gi-high { color: #dc2626; font-weight: 600; }
.stat-chip {
    background: #f0faf0;
    border: 1px solid #c7e0c7;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.82rem;
    color: #1a6b3c;
    font-weight: 500;
    display: inline-block;
    margin: 2px;
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f0f9f0 0%, #e8f5e8 100%);
}
.sidebar-logo {
    font-size: 1.4rem;
    font-weight: 700;
    color: #1a6b3c;
}
/* Nav button styling */
div[data-testid="stRadio"] > label {
    font-size: 0.9rem;
}
/* Profile form card */
.profile-section {
    background: #f9fdfb;
    border: 1px solid #d8edd8;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}
/* Metric cards */
div[data-testid="metric-container"] {
    background: #f0faf0;
    border: 1px solid #d0ead0;
    border-radius: 10px;
    padding: 0.6rem;
}
/* Weekly day header */
.day-badge {
    background: #1a6b3c;
    color: white;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ── Load saved profile ────────────────────────────────────────────────────────
username = st.session_state.get("username", "User")
saved = get_profile(username)

def s(key, default):
    return st.session_state.get(key, saved.get(key, default))

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<div class="sidebar-logo">🥗 NutriSouth AI</div>', unsafe_allow_html=True)
    st.caption(f"👤 Welcome, **{username}**")
    st.divider()

    page = st.radio(
        "Navigation",
        ["🏠 Daily Plan", "📅 Weekly Plan", "🎉 Festival Guide", "👤 Profile"],
        label_visibility="collapsed"
    )

    st.divider()
    # Compact profile summary
    age  = s("age", 45)
    goal = s("goal", "Maintain Weight")
    is_diabetic   = s("is_diabetic", True)
    is_vegetarian = s("is_vegetarian", True)
    spice_tolerance = s("spice_tolerance", "Medium")
    exclude_gluten  = s("exclude_gluten", False)
    exclude_dairy   = s("exclude_dairy", False)
    gender   = s("gender", "Male")
    weight   = s("weight", 70.0)
    height   = s("height", 165.0)
    activity = s("activity", "Sedentary (little/no exercise)")

    st.markdown(f"""
    <div style="font-size:0.82rem;color:#374151;line-height:1.8;">
    🎯 <b>Goal:</b> {goal}<br>
    🩺 <b>Diabetic:</b> {'Yes' if is_diabetic else 'No'}<br>
    🥦 <b>Diet:</b> {'Vegetarian' if is_vegetarian else 'Non-Veg'}<br>
    🌶️ <b>Spice:</b> {spice_tolerance}
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        logout()

# ── Compute nutrition targets ─────────────────────────────────────────────────
bmr            = calculate_bmr(weight, height, age, gender)
tdee           = calculate_tdee(bmr, activity)
target_calories= calculate_target_calories(tdee, goal)
meal_splits    = get_meal_calorie_split(target_calories)
bmi            = calculate_bmi(weight, height)
bmi_cat        = bmi_category(bmi)

# ── Load dish data ────────────────────────────────────────────────────────────
df = load_dishes()

# ── Floating chatbot (shown on all pages) ─────────────────────────────────────
render_floating_chatbot(GROK_API_KEY)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: PROFILE
# ══════════════════════════════════════════════════════════════════════════════
if page == "👤 Profile":
    st.markdown('<p class="main-title">👤 Your Profile</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Update your health details and dietary preferences — your meal plan adjusts automatically.</p>', unsafe_allow_html=True)

    with st.form("profile_form"):
        # ── Personal Details ──────────────────────────────────────────────────
        st.markdown("#### 🧍 Personal Details")
        col1, col2, col3 = st.columns(3)
        with col1:
            f_age    = st.number_input("Age", 18, 90, int(s("age", 45)))
            f_gender = st.selectbox("Gender", ["Male", "Female"],
                        index=["Male","Female"].index(s("gender","Male")))
        with col2:
            f_weight = st.number_input("Weight (kg)", 30.0, 200.0, float(s("weight", 70.0)), step=0.5)
            f_height = st.number_input("Height (cm)", 100.0, 220.0, float(s("height", 165.0)), step=0.5)
        with col3:
            activity_opts = [
                "Sedentary (little/no exercise)",
                "Lightly Active (1-3 days/week)",
                "Moderately Active (3-5 days/week)",
                "Very Active (6-7 days/week)"
            ]
            f_activity = st.selectbox("Activity Level", activity_opts,
                           index=activity_opts.index(s("activity", activity_opts[0])))
            goal_opts  = ["Maintain Weight", "Weight Loss", "Muscle Gain"]
            f_goal     = st.selectbox("Health Goal", goal_opts,
                           index=goal_opts.index(s("goal", "Maintain Weight")))

        st.divider()

        # ── Dietary Preferences ───────────────────────────────────────────────
        st.markdown("#### 🍽️ Dietary Preferences")
        col4, col5, col6 = st.columns(3)
        with col4:
            f_diabetic    = st.toggle("🩺 Diabetic (Type 2)", value=bool(s("is_diabetic", True)))
            f_vegetarian  = st.toggle("🥦 Vegetarian",        value=bool(s("is_vegetarian", True)))
        with col5:
            f_gluten = st.toggle("🌾 Gluten-Free", value=bool(s("exclude_gluten", False)))
            f_dairy  = st.toggle("🥛 Dairy-Free",  value=bool(s("exclude_dairy",  False)))
        with col6:
            f_spice = st.select_slider(
                "🌶️ Spice Tolerance",
                options=["Low", "Medium", "High"],
                value=s("spice_tolerance", "Medium")
            )

        st.divider()

        # ── Save button ───────────────────────────────────────────────────────
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
        with col_btn2:
            submitted = st.form_submit_button(
                "💾 Save Profile",
                use_container_width=True,
                type="primary"
            )

    if submitted:
        profile_data = {
            "age": f_age, "gender": f_gender,
            "weight": f_weight, "height": f_height,
            "activity": f_activity, "goal": f_goal,
            "is_diabetic": f_diabetic, "is_vegetarian": f_vegetarian,
            "spice_tolerance": f_spice,
            "exclude_gluten": f_gluten, "exclude_dairy": f_dairy,
        }
        save_profile(username, profile_data)
        for k, v in profile_data.items():
            st.session_state[k] = v

        # Recompute after save
        bmr2  = calculate_bmr(f_weight, f_height, f_age, f_gender)
        tdee2 = calculate_tdee(bmr2, f_activity)
        tc2   = calculate_target_calories(tdee2, f_goal)
        bmi2  = calculate_bmi(f_weight, f_height)

        st.success("✅ Profile saved successfully!")

        # Stats after save
        st.markdown("#### 📊 Your Updated Stats")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("BMI", f"{bmi2}", bmi_category(bmi2))
        c2.metric("BMR", f"{int(bmr2)} kcal/day")
        c3.metric("Daily Target", f"{int(tc2)} kcal")
        c4.metric("Health Goal", f_goal)
    else:
        # Show current stats
        if saved:
            st.markdown("#### 📊 Current Stats")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("BMI", f"{bmi}", bmi_cat)
            c2.metric("BMR", f"{int(bmr)} kcal/day")
            c3.metric("Daily Target", f"{int(target_calories)} kcal")
            c4.metric("Health Goal", goal)
        else:
            st.info("📝 Fill in your details above and click **Save Profile** to get started.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: DAILY PLAN
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏠 Daily Plan":
    if not saved:
        st.warning("👆 Please set up your **Profile** first before viewing meal plans.")
        st.info("Go to **👤 Profile** in the sidebar to enter your details.")
        st.stop()

    st.markdown('<p class="main-title">🥗 Your Daily Meal Plan</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Personalised South Indian diabetic diet recommendations based on your profile.</p>', unsafe_allow_html=True)

    # ── Stats row ─────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🔥 Daily Target", f"{int(target_calories)} kcal")
    c2.metric("📊 BMI",          f"{bmi} ({bmi_cat})")
    c3.metric("🍳 Breakfast",    f"{meal_splits['breakfast']} kcal")
    c4.metric("🍛 Lunch",        f"{meal_splits['lunch']} kcal")
    c5.metric("🌙 Dinner",       f"{meal_splits['dinner']} kcal")

    st.divider()

    def render_meal_section(label, key, icon):
        st.markdown(f"<div class='section-header'>{icon} {label} &nbsp;<small style='font-weight:400;color:#6b7280;'>Target: {meal_splits[key]} kcal</small></div>", unsafe_allow_html=True)

        recs = recommend_dishes(
            df=df, meal_type=key, calorie_target=meal_splits[key],
            is_diabetic=is_diabetic, is_vegetarian=is_vegetarian,
            spice_tolerance=spice_tolerance, exclude_gluten=exclude_gluten,
            exclude_dairy=exclude_dairy, goal=goal, n=3
        )

        if recs is None or recs.empty:
            st.warning(f"No dishes found for {label}. Try adjusting your preferences in Profile.")
            return

        cols = st.columns(len(recs))
        for i, (_, row) in enumerate(recs.iterrows()):
            gi_class = f"gi-{row['gi_category'].lower()}"
            with cols[i]:
                st.markdown(f"""
                <div class="meal-card">
                    <div class="dish-name">{row['dish_name']}</div>
                    <div style="font-size:0.78rem;color:#6b7280;margin:3px 0 8px;">{row['serving_size']}</div>
                    <div style="font-size:0.88rem;margin-bottom:6px;">
                        🔥 <b>{int(row['calories'])} kcal</b>
                        &nbsp;|&nbsp;
                        <span class="{gi_class}">GI: {row['gi_category']}</span>
                    </div>
                    <div style="font-size:0.8rem;color:#374151;line-height:1.7;">
                        🥩 <b>{row['protein_g']}g</b> protein &nbsp;
                        🍞 <b>{row['carbs_g']}g</b> carbs<br>
                        🧈 <b>{row['fat_g']}g</b> fat &nbsp;&nbsp;
                        🌾 <b>{row['fiber_g']}g</b> fiber
                    </div>
                    <div style="font-size:0.76rem;color:#16a34a;margin-top:8px;border-top:1px solid #e5f0e5;padding-top:6px;">
                        ✅ {build_reason(row, goal, is_diabetic)}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    render_meal_section("Breakfast", "breakfast", "🍳")
    render_meal_section("Lunch",     "lunch",      "🍛")
    render_meal_section("Dinner",    "dinner",     "🌙")
    render_meal_section("Snack",     "snack",      "🥜")

    # ── Macro Summary ─────────────────────────────────────────────────────────
    st.divider()
    st.markdown("<div class='section-header'>📊 Daily Nutrition Summary</div>", unsafe_allow_html=True)

    all_recs = []
    for mk in ["breakfast","lunch","dinner","snack"]:
        r = recommend_dishes(df, mk, meal_splits[mk], is_diabetic, is_vegetarian,
                             spice_tolerance, exclude_gluten, exclude_dairy, goal, n=1)
        if r is not None and not r.empty:
            all_recs.append(r.iloc[0])

    if all_recs:
        summary      = pd.DataFrame(all_recs)
        total_cal    = summary["calories"].sum()
        total_protein= summary["protein_g"].sum()
        total_carbs  = summary["carbs_g"].sum()
        total_fat    = summary["fat_g"].sum()
        total_fiber  = summary["fiber_g"].sum()

        col_left, col_right = st.columns([3, 2])
        with col_left:
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Calories",  f"{int(total_cal)}")
            m2.metric("Protein",   f"{round(total_protein,1)}g")
            m3.metric("Carbs",     f"{round(total_carbs,1)}g")
            m4.metric("Fat",       f"{round(total_fat,1)}g")
            m5.metric("Fiber",     f"{round(total_fiber,1)}g")
            progress = min(total_cal / target_calories, 1.0)
            st.markdown(f"**Calorie Goal Progress: {int(total_cal)} / {int(target_calories)} kcal**")
            st.progress(progress)
        with col_right:
            fig, ax = plt.subplots(figsize=(3.5, 3.5))
            sizes  = [total_protein*4, total_carbs*4, total_fat*9]
            colors = ["#16a34a","#3b82f6","#f59e0b"]
            wedges, texts, autotexts = ax.pie(
                sizes, labels=["Protein","Carbs","Fat"],
                colors=colors, autopct="%1.0f%%",
                startangle=90, textprops={"fontsize":10}
            )
            ax.set_title("Macros", fontsize=11, fontweight="bold")
            fig.patch.set_facecolor("none")
            st.pyplot(fig)
            plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: WEEKLY PLAN
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📅 Weekly Plan":
    if not saved:
        st.warning("👆 Please set up your **Profile** first.")
        st.info("Go to **👤 Profile** in the sidebar.")
        st.stop()

    st.markdown('<p class="main-title">📅 Your Weekly Meal Plan</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">7-day South Indian diabetic meal plan — every day gets a different dish.</p>', unsafe_allow_html=True)

    with st.spinner("Generating your 7-day plan..."):
        weekly = generate_weekly_plan(
            df=df, meal_calorie_split=meal_splits,
            is_diabetic=is_diabetic, is_vegetarian=is_vegetarian,
            spice_tolerance=spice_tolerance, exclude_gluten=exclude_gluten,
            exclude_dairy=exclude_dairy, goal=goal
        )

    meal_icons = {"breakfast":"🍳","lunch":"🍛","dinner":"🌙","snack":"🥜"}

    for day, meals in weekly.items():
        with st.expander(f"📆  {day}", expanded=(day == "Monday")):
            cols = st.columns(4)
            for i, (meal, recs) in enumerate(meals.items()):
                with cols[i]:
                    st.markdown(f"**{meal_icons[meal]} {meal.capitalize()}**")
                    if recs is not None and not recs.empty:
                        row = recs.iloc[0]
                        gi_class = f"gi-{row['gi_category'].lower()}"
                        st.markdown(f"""
                        <div class="meal-card" style="padding:0.8rem;">
                            <div class="dish-name" style="font-size:0.9rem;">{row['dish_name']}</div>
                            <div style="font-size:0.75rem;color:#6b7280;margin-top:2px;">{row['serving_size']}</div>
                            <div style="font-size:0.8rem;margin-top:6px;">
                                🔥 {int(row['calories'])} kcal
                                &nbsp;|&nbsp;
                                <span class="{gi_class}">GI: {row['gi_category']}</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.info("No match")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: FESTIVAL GUIDE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🎉 Festival Guide":
    st.markdown('<p class="main-title">🎉 Festival Diet Guide</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-subtitle">Diabetic-friendly alternatives for popular South Indian festival foods.</p>', unsafe_allow_html=True)

    festival = st.selectbox("Select a Festival", list_festivals())
    plan = get_festival_plan(festival)

    if plan:
        st.markdown(f"### 🪔 {festival}")
        st.info(plan.get("description",""))

        st.markdown("#### 🥗 Diabetic-Friendly Alternatives")
        cols = st.columns(2)
        for idx, item in enumerate(plan.get("diabetic_friendly_alternatives",[])):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class="meal-card">
                    <div class="dish-name">{item['dish']}</div>
                    <div style="font-size:0.84rem;color:#444;margin-top:5px;">💡 {item['note']}</div>
                </div>
                """, unsafe_allow_html=True)

        st.divider()
        st.markdown("""
        > **General Festival Tips for Diabetics:**
        > - Keep portions small — taste everything, overeat nothing
        > - Prefer baked or steamed over fried
        > - Swap white rice with millet or ragi wherever possible
        > - Replace sugar with small amounts of jaggery or stevia
        > - Stay hydrated with buttermilk, neer mor, or coconut water
        > - Check blood sugar more frequently on festival days
        """)
