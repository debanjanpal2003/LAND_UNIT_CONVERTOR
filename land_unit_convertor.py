import streamlit as st

st.set_page_config(page_title="Land Unit Converter", layout="centered")

# Conversion constants (West Bengal / Bihar standard)
SQFT_PER_DECIMAL = 435.6
SQFT_PER_KATHA   = 720
SQFT_PER_CHATAK  = 45
SQFT_PER_BIGHA   = 14400
KATHA_PER_ACRE   = 60.5

# Master unit = SQFT
def to_sqft(value, unit):
    unit = unit.lower()
    if unit == "sqft":
        return value
    if unit == "decimal":
        return value * SQFT_PER_DECIMAL
    if unit == "chatak":
        return value * SQFT_PER_CHATAK
    if unit == "katha":
        return value * SQFT_PER_KATHA
    if unit == "bigha":
        return value * SQFT_PER_BIGHA
    if unit == "acre":
        return value * (SQFT_PER_KATHA * KATHA_PER_ACRE)
    return 0


def from_sqft(sqft):
    acre   = sqft / (SQFT_PER_KATHA * KATHA_PER_ACRE)
    bigha  = sqft / SQFT_PER_BIGHA
    katha  = sqft / SQFT_PER_KATHA
    chatak = sqft / SQFT_PER_CHATAK
    decimal = sqft / SQFT_PER_DECIMAL
    return acre, bigha, katha, chatak, decimal


def hierarchy_breakdown(sqft):
    remaining = sqft

    # Acre
    acre = int(remaining // (SQFT_PER_KATHA * KATHA_PER_ACRE))
    remaining -= acre * (SQFT_PER_KATHA * KATHA_PER_ACRE)

    # Bigha
    bigha = int(remaining // SQFT_PER_BIGHA)
    remaining -= bigha * SQFT_PER_BIGHA

    # Katha
    katha = int(remaining // SQFT_PER_KATHA)
    remaining -= katha * SQFT_PER_KATHA

    # Chatak
    chatak = int(remaining // SQFT_PER_CHATAK)
    remaining -= chatak * SQFT_PER_CHATAK

    # Decimal (float)
    decimal = round(remaining / SQFT_PER_DECIMAL, 5)

    return acre, bigha, katha, chatak, decimal


# Streamlit UI
st.title("🌐 Land Unit Converter (India)")
st.write("Convert Acre, Bigha, Katha, Chatak, Decimal, Sq.Ft with hierarchy breakdown.")

unit_list = ["acre", "bigha", "katha", "chatak", "decimal", "sqft"]

value = st.number_input("Enter value:", min_value=0.0, format="%.4f")
unit  = st.selectbox("Select unit:", unit_list)

if st.button("Convert"):
    sqft = to_sqft(value, unit)

    # FULL CONVERSION (NEW FEATURE)
    acre, bigha, katha, chatak, decimal = from_sqft(sqft)

    st.subheader("📌 FULL UNIT CONVERSION")
    st.write(f"### {value} {unit} =")
    st.write(f"- **Acre:** {acre:.6f}")
    st.write(f"- **Bigha:** {bigha:.6f}")
    st.write(f"- **Katha:** {katha:.6f}")
    st.write(f"- **Chatak:** {chatak:.6f}")
    st.write(f"- **Decimal:** {decimal:.6f}")
    st.write(f"- **Sq.Ft:** {sqft:.2f}")

    # HIERARCHY BREAKDOWN (old feature)
    st.subheader("📐 HIERARCHY BREAKDOWN (Acre → Bigha → Katha → Chatak → Decimal)")
    h_acre, h_bigha, h_katha, h_chatak, h_decimal = hierarchy_breakdown(sqft)

    st.write(f"- Acre: `{h_acre}`")
    st.write(f"- Bigha: `{h_bigha}`")
    st.write(f"- Katha: `{h_katha}`")
    st.write(f"- Chatak: `{h_chatak}`")
    st.write(f"- Decimal: `{h_decimal}`")
    st.info("Note: This breakdown computes whole counts of each larger unit and expands the leftover into smaller units. "
        "The 'decimal' line will show any fractional decimal (less than 1) as a decimal fraction and its approx sq.ft value; final leftover is shown in sq.ft.")
