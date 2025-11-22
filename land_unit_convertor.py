# app.py
import streamlit as st
from math import floor

st.set_page_config(page_title="Land Unit Converter & Hierarchical Breakdown", layout="centered")

# Canonical values in square-feet (based on your inputs)
UNITS_SQFT = {
    "acre": 43560.0,
    "bigha": 14400.0,
    "katha": 720.0,
    "chatak": 45.0,
    "decimal": 435.6,
    "sq.ft": 1.0
}

HIERARCHY = ["acre", "bigha", "katha", "chatak", "decimal", "sq.ft"]

UNIT_LABELS = {
    "acre": "Acre",
    "bigha": "Bigha",
    "katha": "Katha",
    "chatak": "Chatak",
    "decimal": "Decimal",
    "sq.ft": "Sq.ft"
}

def to_sqft(value: float, unit: str) -> float:
    return value * UNITS_SQFT[unit]

def from_sqft(sqft: float, unit: str) -> float:
    return sqft / UNITS_SQFT[unit]

def hierarchical_breakdown(value: float, unit: str):
    """
    Convert input value (in `unit`) to a hierarchical breakdown
    using HIERARCHY list (top -> bottom).
    Returns list of tuples: (unit, integer_count, fractional_of_unit, remainder_sqft_for_unit)
    where fractional_of_unit applies only to the 'decimal' level (smaller-than-integer decimals).
    """
    total_sqft = to_sqft(value, unit)
    remaining_sqft = total_sqft
    breakdown = []

    for u in HIERARCHY:
        u_sqft = UNITS_SQFT[u]
        if u != "decimal":  # for all except decimal, take integer count
            count = int(remaining_sqft // u_sqft)
            breakdown.append({
                "unit": u,
                "count": count,
                "frac": 0.0,
                "remainder_sqft": remaining_sqft - (count * u_sqft)
            })
            remaining_sqft = remaining_sqft - (count * u_sqft)
        else:
            # For decimal, we want integer decimal count + fractional decimal part (converted to sq.ft)
            int_dec = int(remaining_sqft // u_sqft)
            rem_after_dec = remaining_sqft - int_dec * u_sqft
            # fractional decimal expressed as decimal units (less than 1)
            frac_decimal = rem_after_dec / u_sqft if u_sqft != 0 else 0.0
            breakdown.append({
                "unit": u,
                "count": int_dec,
                "frac": frac_decimal,
                "remainder_sqft": rem_after_dec  # this is the leftover sq.ft smaller than 1 decimal
            })
            remaining_sqft = rem_after_dec

    # after loop, remaining_sqft should be < 1 decimal (i.e., leftover sq.ft)
    # The last item in breakdown corresponds to 'sq.ft' integer count:
    # Replace last item (sq.ft) with exact integer sqft and any fractional (should be zero)
    sqft_unit = breakdown[-1]
    sqft_count = int(round(remaining_sqft))  # round tiny floating noise
    sqft_unit["count"] = sqft_count
    sqft_unit["remainder_sqft"] = remaining_sqft - sqft_count
    # fractional for sq.ft stays 0
    return breakdown, total_sqft

def pretty_number(x: float, max_decimals=6):
    if abs(x) >= 1:
        s = f"{x:,.{max_decimals}f}"
        # strip trailing zeros
        s = s.rstrip('0').rstrip('.')
        return s
    else:
        s = f"{x:.8f}"
        s = s.rstrip('0').rstrip('.')
        return s if s != "" else "0"

# -- UI --
st.title("Land Unit Converter — Any→Any + Hierarchical Breakdown")
st.markdown("Convert between Acre, Bigha, Katha, Chatak, Decimal and Sq.ft and see the expansion into smaller units (breakdown).")

col1, col2 = st.columns([2,2])
with col1:
    from_unit = st.selectbox("Input unit", HIERARCHY, index=1, format_func=lambda u: UNIT_LABELS[u])
with col2:
    to_unit = st.selectbox("Convert to unit (any)", HIERARCHY[::-1], index=0, format_func=lambda u: UNIT_LABELS[u])

value = st.number_input("Input value", min_value=0.0, value=1.0, step=0.01, format="%.6f")

# Instant conversion
converted = from_sqft(to_sqft(value, from_unit), to_unit)
st.markdown(f"**Conversion:** {pretty_number(value)} {UNIT_LABELS[from_unit]} = **{pretty_number(converted)} {UNIT_LABELS[to_unit]}**")

st.markdown("---")
st.subheader("Hierarchical breakdown (top → bottom)")

breakdown, total_sqft = hierarchical_breakdown(value, from_unit)

# Present the breakdown nicely
st.markdown(f"**Total area:** {pretty_number(total_sqft)} sq.ft")

lines = []
for item in breakdown:
    u = item["unit"]
    name = UNIT_LABELS[u]
    count = item["count"]
    frac = item.get("frac", 0.0)
    rem_sqft = item["remainder_sqft"]

    if u == "decimal":
        # show integer decimals + fractional decimal (converted to decimal value) + leftover sqft
        if count:
            lines.append(f"{count} {name}")
        if frac and frac > 0:
            # fractional decimal e.g. 0.27 decimal
            lines.append(f"+ {pretty_number(frac)} {name} (≈ {pretty_number(frac * UNITS_SQFT['decimal'])} sq.ft)")
        if rem_sqft and rem_sqft > 0:
            # this rem_sqft is what's left under 1 decimal; final leftover will be shown in sq.ft row
            lines.append(f"+ {pretty_number(rem_sqft)} sq.ft (leftover)")
    elif u == "sq.ft":
        if count:
            lines.append(f"+ {pretty_number(count)} sq.ft")
        # if there is a tiny fractional remainder (should be ~0), show it
        tiny = item["remainder_sqft"]
        if abs(tiny) > 1e-6:
            lines.append(f"+ {pretty_number(tiny)} sq.ft (fractional leftover)")
    else:
        if count:
            lines.append(f"{count} {name}")

# Display as monospace block for readability
st.code("\n".join(lines), language=None)

st.markdown("---")
st.markdown("**Unit definitions used:**")
for u in HIERARCHY:
    st.write(f"- {UNIT_LABELS[u]} = {pretty_number(UNITS_SQFT[u])} sq.ft")

st.info("Note: This breakdown computes whole counts of each larger unit and expands the leftover into smaller units. "
        "The 'decimal' line will show any fractional decimal (less than 1) as a decimal fraction and its approx sq.ft value; final leftover is shown in sq.ft.")
