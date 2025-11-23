import streamlit as st
import pandas as pd

# -------------------------
# Language text
# -------------------------
TEXT = {
    "en": {
        "title": "Land Unit Converter",
        "select_unit": "Select input unit:",
        "enter_value": "Enter value:",
        "convert": "Convert",
        "all_units": "Converted Values (All Units)",
        "full_breakdown": "Hierarchy Breakdown (Acre → Bigha → Katha → Chatak → Decimal)",
        "definitions": "Unit Definitions",
        "sqft": "Sq.ft",
        "acre": "Acre",
        "bigha": "Bigha",
        "katha": "Katha",
        "chatak": "Chatak",
        "decimal": "Decimal",
        "note": ("Note: This breakdown computes whole counts of each larger unit and "
                 "expands the leftover into smaller units. The 'decimal' line may show fractional decimal values (<1)"),
        # Division texts
        "division": "Land Division",
        "enable_div": "Enable Division",
        "num_parts": "Number of parts",
        "ratio_input": "Ratio for part {i}",
        "normalize_option": "Auto-normalize ratios if sum ≠ 1",
        "ratio_error": "Error: total ratio must be > 0 (or enable normalization).",
        "ratio_sum_not_one": "Note: ratios normalized (sum was {s}).",
        "division_results": "Division Results",
        "person": "Person",
        "ratio": "Ratio",
        "copy_ok": "Copied to clipboard (if supported).",
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
        "note": ("নোট: এই ভাঙনটি বড় ইউনিটগুলোকে প্রথমে পূর্ণ সংখ্যায় গণনা করে এবং "
                 "বাকি অংশগুলোকে ছোট ইউনিটে রূপান্তর করে। 'ডেসিমেল' লাইনে ১-এর কম ভগ্নাংশ দেখানো হতে পারে।"),
        # Division texts
        "division": "জমি ভাগ",
        "enable_div": "ভাগ সক্রিয় করুন",
        "num_parts": "কত ভাগ করবেন",
        "ratio_input": "ভাগ {i} এর অনুপাত",
        "normalize_option": "স্বয়ংক্রিয়ভাবে স্বাভাবিককরণ (যদি যোগফল ≠ 1)",
        "ratio_error": "ত্রুটি: মোট অনুপাত শূন্যের বড় হতে হবে (অথবা স্বাভাবিককরণ সক্রিয় করুন)।",
        "ratio_sum_not_one": "নোট: অনুপাতগুলো স্বাভাবিককরণ করা হয়েছে (যোগফল ছিল {s})।",
        "division_results": "ভাগের ফলাফল",
        "person": "ব্যক্তি",
        "ratio": "অনুপাত",
        "copy_ok": "কপি হয়েছে (যদি ব্রাউজার সাপোর্ট করে)।",
    }
}

# -------------------------
# Unit constants (sq.ft)
# -------------------------
UNITS_SQFT = {
    "acre": 43560.0,
    "bigha": 14400.0,
    "katha": 720.0,     # user-specified
    "chatak": 45.0,
    "decimal": 435.6,
}
# hierarchy for breakdown display (Acre -> Bigha -> Katha -> Chatak -> Decimal)
HIERARCHY = ["acre", "bigha", "katha", "chatak", "decimal"]

# -------------------------
# helpers
# -------------------------
def to_sqft(value, unit):
    return value * UNITS_SQFT[unit]

def sqft_to_all(sqft):
    return {
        "sqft": sqft,
        "decimal": sqft / UNITS_SQFT["decimal"],
        "chatak": sqft / UNITS_SQFT["chatak"],
        "katha": sqft / UNITS_SQFT["katha"],
        "bigha": sqft / UNITS_SQFT["bigha"],
        "acre": sqft / UNITS_SQFT["acre"],
    }

def pretty(n, d=6):
    try:
        s = f"{float(n):.{d}f}"
        s = s.rstrip("0").rstrip(".")
        return s if s != "" else "0"
    except:
        return "0"

# -------------------------
# Streamlit page
# -------------------------
st.set_page_config(page_title="Land Converter", layout="centered")

# language toggle
lang_choice = st.radio("Language / ভাষা", ("English", "বাংলা"))
lang = "bn" if lang_choice == "বাংলা" else "en"
T = TEXT[lang]

st.title(T["title"])

# Input area
unit = st.selectbox(T["select_unit"], list(UNITS_SQFT.keys()), format_func=lambda u: T[u])
value = st.number_input(T["enter_value"], min_value=0.0, step=0.1, format="%.4f")

# session state to persist that user clicked Convert
if "converted" not in st.session_state:
    st.session_state.converted = False
    st.session_state.last_sqft = None
    st.session_state.last_value = None
    st.session_state.last_unit = None

if st.button(T["convert"]):
    # compute and remember
    sqft_val = to_sqft(value, unit)
    st.session_state.converted = True
    st.session_state.last_sqft = sqft_val
    st.session_state.last_value = value
    st.session_state.last_unit = unit

# Only show conversion & division area after user clicked Convert
if st.session_state.converted and st.session_state.last_sqft is not None:
    sqft_val = st.session_state.last_sqft

    # 1) All unit conversions
    st.subheader(T["all_units"])
    all_vals = sqft_to_all(sqft_val)
    # display in the requested table/order: Sq.ft | Decimal | Chatak | Katha | Bigha | Acre
    st.write(f"- **{T['sqft']}:** {pretty(all_vals['sqft'],4)}")
    st.write(f"- **{T['decimal']}:** {pretty(all_vals['decimal'],6)}")
    st.write(f"- **{T['chatak']}:** {pretty(all_vals['chatak'],6)}")
    st.write(f"- **{T['katha']}:** {pretty(all_vals['katha'],6)}")
    st.write(f"- **{T['bigha']}:** {pretty(all_vals['bigha'],6)}")
    st.write(f"- **{T['acre']}:** {pretty(all_vals['acre'],6)}")

    st.markdown("---")

    # 2) Hierarchy breakdown (Acre -> Bigha -> Katha -> Chatak -> Decimal)
    st.subheader(T["full_breakdown"])
    remaining = sqft_val
    breakdown_lines = []
    for u in HIERARCHY:
        unit_count = int(remaining // UNITS_SQFT[u])
        remaining -= unit_count * UNITS_SQFT[u]
        breakdown_lines.append(f"{T[u]}: {unit_count}")
    st.code("\n".join(breakdown_lines), language=None)

    st.markdown("---")

    # 3) DIVISION SECTION (appears after Convert)
    st.subheader(T["division"])
    enable_div = st.checkbox(T["enable_div"])

    if enable_div:
        parts = st.number_input(T["num_parts"], min_value=1, step=1, value=2)
        # normalize option
        normalize = st.checkbox(T["normalize_option"])
        # gather ratios inputs
        ratios = []
        cols = st.columns(min(6, parts))  # layout for many parts
        # We must create stable keys for inputs
        for i in range(1, parts + 1):
            key = f"ratio_{i}"
            # place inputs in columns cyclically
            col = cols[(i-1) % len(cols)]
            r = col.number_input(T["ratio_input"].replace("{i}", str(i)), min_value=0.0, step=0.01, value=0.0, key=key)
            ratios.append(r)

        sum_ratios = sum(ratios)

        if sum_ratios <= 0:
            st.error(T["ratio_error"])
        else:
            normalized_ratios = ratios
            normalized_note = None
            if abs(sum_ratios - 1.0) > 1e-9:
                if normalize:
                    normalized_ratios = [r / sum_ratios for r in ratios]
                    normalized_note = T["ratio_sum_not_one"].format(s=pretty(sum_ratios,6))
                else:
                    st.warning(T["ratio_sum_not_one"].format(s=pretty(sum_ratios,6)) + " " + ("Enable normalization or adjust ratios." if lang=="en" else "স্বাভাবিককরণ সক্রিয় করুন বা অনুপাত সংশোধন করুন।"))

            # Show results only if normalized or exact (if normalization not enabled require equality)
            if normalize or abs(sum_ratios - 1.0) <= 1e-9:
                # build results rows
                rows = []
                for idx, r in enumerate(normalized_ratios, start=1):
                    share_sqft = sqft_val * r
                    all_share = sqft_to_all(share_sqft)
                    row = {
                        T["person"]: f"{T['person']} {idx}",
                        T["ratio"]: pretty(r,6),
                        T["sqft"]: pretty(all_share["sqft"],4),
                        T["decimal"]: pretty(all_share["decimal"],6),
                        T["chatak"]: pretty(all_share["chatak"],6),
                        T["katha"]: pretty(all_share["katha"],6),
                        T["bigha"]: pretty(all_share["bigha"],6),
                        T["acre"]: pretty(all_share["acre"],6),
                    }
                    rows.append(row)

                df = pd.DataFrame(rows)
                st.subheader(T["division_results"])
                st.table(df)  # nice formatted table

                if normalized_note:
                    st.info(normalized_note)

    st.markdown("---")

    # 4) Definitions (unchanged)
    st.subheader(T["definitions"])
    for u in HIERARCHY:
        st.write(f"- **{T[u]}** = {pretty(UNITS_SQFT[u],4)} {T['sqft']}")

    st.info(T["note"])
