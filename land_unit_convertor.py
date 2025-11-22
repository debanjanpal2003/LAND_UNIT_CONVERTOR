import streamlit as st

# -------------------------------------------
# Language packs
# -------------------------------------------
TEXT = {
    "en": {
        "title": "Land Unit Converter",
        "select_unit": "Select input unit:",
        "enter_value": "Enter value:",
        "convert": "Convert",
        "all_units": "Converted Values (All Units)",
        "full_breakdown": "Hierarchy Breakdown (Acre → Bigha → Katha → Chatak → Decimal)",
        "definitions": "Unit Definitions",
        "sqft": "sq.ft",
        "acre": "Acre",
        "bigha": "Bigha",
        "katha": "Katha",
        "chatak": "Chatak",
        "decimal": "Decimal",
        "note": "Note: This breakdown computes whole counts of each larger unit and expands the leftover into smaller units. The 'decimal' line may show fractional decimal values (<1) and its approximate sq.ft value. Final leftover is shown in sq.ft.",
    },
    "bn": {
        "title": "জমির ইউনিট রূপান্তর",
        "select_unit": "ইউনিট নির্বাচন করুন:",
        "enter_value": "মান লিখুন:",
        "convert": "রূপান্তর করুন",
        "all_units": "সমস্ত ইউনিটে রূপান্তরিত মান",
        "full_breakdown": "ক্রম অনুযায়ী ভাঙ্গন (একর → বিঘা → কাঠা → ছটাক → ডেসিমেল)",
        "definitions": "ইউনিট সংজ্ঞা",
        "sqft": "স্কয়ার ফুট",
        "acre": "একর",
        "bigha": "বিঘা",
        "katha": "কাঠা",
        "chatak": "ছটাক",
        "decimal": "ডেসিমেল",
        "note": "নোট: এই ভাঙন পদ্ধতিতে বড় ইউনিটগুলো প্রথমে পূর্ণ সংখ্যায় গণনা করা হয় এবং বাকি অংশ ছোট ইউনিটে রূপান্তর করা হয়। 'ডেসিমেল' লাইনে ১-এর কম ভগ্নাংশ থাকতে পারে এবং তার আনুমানিক স্কয়ার ফুট মান দেখানো হয়। শেষ বাকি অংশ স্কয়ার ফুট হিসেবে দেখানো হয়।",
    }
}

# -------------------------------------------
# Unit conversion (all based on sq.ft)
# -------------------------------------------
UNITS_SQFT = {
    "acre": 43560,
    "bigha": 14400,
    "katha": 720,
    "chatak": 45,
    "decimal": 435.6,
}

HIERARCHY = ["acre", "bigha", "katha", "chatak", "decimal"]

def convert_to_sqft(value, unit):
    return value * UNITS_SQFT[unit]

def sqft_to_all_units(sqft):
    return {
        u: sqft / UNITS_SQFT[u] for u in UNITS_SQFT
    }

def pretty(x):
    return f"{x:.6f}".rstrip("0").rstrip(".")

# -------------------------------------------
# Streamlit UI
# -------------------------------------------
st.set_page_config(page_title="Land Converter", layout="centered")

# Language toggle
lang = st.radio("Language / ভাষা", ("English", "বাংলা"))
L = TEXT["bn"] if lang == "বাংলা" else TEXT["en"]

st.title(L["title"])

# Input section
unit = st.selectbox(L["select_unit"], HIERARCHY, format_func=lambda u: L[u])
value = st.number_input(L["enter_value"], min_value=0.0, step=0.1)

if st.button(L["convert"]):

    # Convert to sqft
    sqft_val = convert_to_sqft(value, unit)

    # ----------------------------------------------------
    # 1) Show ALL unit conversions
    # ----------------------------------------------------
    st.subheader(L["all_units"])
    all_vals = sqft_to_all_units(sqft_val)

    st.write(f"- **{L['acre']}:** {pretty(all_vals['acre'])}")
    st.write(f"- **{L['bigha']}:** {pretty(all_vals['bigha'])}")
    st.write(f"- **{L['katha']}:** {pretty(all_vals['katha'])}")
    st.write(f"- **{L['chatak']}:** {pretty(all_vals['chatak'])}")
    st.write(f"- **{L['decimal']}:** {pretty(all_vals['decimal'])}")
    st.write(f"- **{L['sqft']}:** {pretty(sqft_val)}")

    st.markdown("---")

    # ----------------------------------------------------
    # 2) Hierarchy breakdown (Acre → Bigha → Katha → Chatak → Decimal)
    # ----------------------------------------------------
    st.subheader(L["full_breakdown"])

    remaining = sqft_val
    lines = []

    for u in HIERARCHY:
        unit_count = int(remaining // UNITS_SQFT[u])
        remaining -= unit_count * UNITS_SQFT[u]
        lines.append(f"{L[u]}: {unit_count}")

    # Display block
    st.code("\n".join(lines), language=None)

    st.markdown("---")

    # ----------------------------------------------------
    # 3) Unit Definitions
    # ----------------------------------------------------
    st.subheader(L["definitions"])
    for u in HIERARCHY:
        st.write(f"- **{L[u]}** = {pretty(UNITS_SQFT[u])} {L['sqft']}")
    
    st.info(L["note"])
