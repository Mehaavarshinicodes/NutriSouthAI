FESTIVAL_DISHES = {
    "Pongal (Thai Pongal)": {
        "description": "Harvest festival of Tamil Nadu",
        "diabetic_friendly_alternatives": [
            {"dish": "Ragi Pongal", "note": "Made with ragi instead of white rice — lower GI"},
            {"dish": "Millet Pongal (Thinai)", "note": "Foxtail millet pongal — diabetic-friendly"},
            {"dish": "Sakkarai Pongal (Sugar-free)", "note": "Use stevia or jaggery in small amounts"},
            {"dish": "Ven Pongal with less ghee", "note": "Savory pongal in moderate portions"},
        ]
    },
    "Diwali": {
        "description": "Festival of lights",
        "diabetic_friendly_alternatives": [
            {"dish": "Ragi Ladoo (Sugar-free)", "note": "Made with ragi, jaggery substitute, and nuts"},
            {"dish": "Roasted Chana Mixture", "note": "High protein, low sugar snack"},
            {"dish": "Baked Murukku (low oil)", "note": "Baked instead of fried"},
            {"dish": "Dates and Nut Barfi", "note": "Natural sweetener, high fiber"},
        ]
    },
    "Onam": {
        "description": "Kerala harvest festival",
        "diabetic_friendly_alternatives": [
            {"dish": "Onam Sadya (modified)", "note": "Focus on Avial, Olan, Thoran — avoid payasam"},
            {"dish": "Kaalan (less coconut)", "note": "Yam/raw banana curry — moderate portions"},
            {"dish": "Injipuli", "note": "Tamarind-ginger curry — no sugar"},
            {"dish": "Millet Payasam (sugar-free)", "note": "Use coconut milk and stevia"},
        ]
    },
    "Navratri": {
        "description": "Nine nights festival",
        "diabetic_friendly_alternatives": [
            {"dish": "Sabudana Khichdi (small portion)", "note": "High GI — keep portions very small"},
            {"dish": "Kuttu Roti", "note": "Buckwheat flatbread — lower GI than wheat"},
            {"dish": "Peanut Salad", "note": "High protein fasting snack"},
            {"dish": "Fruit Salad (no banana)", "note": "Choose low-GI fruits like guava, papaya"},
        ]
    },
    "Ugadi / Tamil New Year": {
        "description": "New Year festival for South Indians",
        "diabetic_friendly_alternatives": [
            {"dish": "Ugadi Pachadi (small portion)", "note": "Traditional 6-taste dish — have a small taste only"},
            {"dish": "Millet Pulihora", "note": "Tamarind rice with millet instead of white rice"},
            {"dish": "Pesarattu", "note": "Green moong dosa — high protein, diabetic-friendly"},
            {"dish": "Neem Flower Rasam", "note": "Bittersweet — good for blood sugar"},
        ]
    }
}

def get_festival_plan(festival_name: str) -> dict:
    return FESTIVAL_DISHES.get(festival_name, {})

def list_festivals() -> list:
    return list(FESTIVAL_DISHES.keys())
