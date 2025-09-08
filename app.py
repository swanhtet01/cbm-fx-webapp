
import streamlit as st
import math
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Export FX — CBM vs Black", page_icon="🌍", layout="wide")

# --- Helpers ---
def blended_rate(p1_pct, r1, r2):
    p1 = p1_pct / 100.0
    return p1 * r1 + (1 - p1) * r2

def mmk_with_split(usd, p1_pct, r1, r2, flat_fee=0.0, pct_fee=0.0):
    rate = blended_rate(p1_pct, r1, r2)
    return usd * rate - flat_fee - (pct_fee * usd * r2)

def mmk_full_black(usd, r2, flat_fee=0.0, pct_fee=0.0):
    return usd * r2 - flat_fee - (pct_fee * usd * r2)

def fmt_mmk(x):
    try:
        return f"{x:,.0f} MMK"
    except:
        return "—"

def fmt_rate(x):
    try:
        return f"{x:,.2f} MMK/USD"
    except:
        return "—"

def fmt_pct(x):
    try:
        return f"{x*100:,.2f}%"
    except:
        return "—"

st.title("🌍 Export FX — CBM Split vs Full Black (Super Simple Web App)")

# ============ SIDEBAR (Inputs) ============
st.sidebar.header("Inputs (Adjust)")

col_usd, col_p1 = st.sidebar.columns(2)
usd = col_usd.number_input("Total export (USD)", min_value=0.0, value=100000.0, step=1000.0, format="%.2f")
p1_pct = col_p1.slider("Official share p₁ (%)", min_value=0, max_value=100, value=25, step=1)

col_rates = st.sidebar.columns(2)
r1 = col_rates[0].number_input("Official rate r₁ (MMK/USD)", min_value=0.0, value=2100.0, step=50.0, format="%.2f")
r2 = col_rates[1].number_input("Black rate r₂ (MMK/USD)", min_value=0.0, value=4150.0, step=50.0, format="%.2f")

st.sidebar.markdown("---")
st.sidebar.caption("Optional fees (applied to both scenarios)")
fee_flat = st.sidebar.number_input("Flat fee (MMK)", min_value=0.0, value=0.0, step=10000.0, format="%.2f")
fee_pct = st.sidebar.number_input("% fee on USD (as decimal, e.g., 0.005 = 0.5%)", min_value=0.0, value=0.0, step=0.001, format="%.3f")

st.sidebar.markdown("---")
target_pct_black = st.sidebar.slider("Target % of black you want to achieve", min_value=50, max_value=100, value=90, step=1)

# ============ MAIN: CALCULATIONS ============
rate_eff = blended_rate(p1_pct, r1, r2)
mmk_split = mmk_with_split(usd, p1_pct, r1, r2, fee_flat, fee_pct)
mmk_black = mmk_full_black(usd, r2, fee_flat, fee_pct)
shortfall = mmk_black - mmk_split
pct_of_black = (rate_eff / r2) if r2 else float("nan")
pct_shortfall = 1 - pct_of_black if r2 else float("nan")

# Threshold analytics
# r2_needed = (r2 - p1*r1) / (1 - p1)  [derived earlier, but here we want r_eff target or p1_max for target]
p1_frac = p1_pct/100.0 if p1_pct is not None else 0.0
r2_needed_to_be_whole = (r2 - p1_frac * r1) / (1 - p1_frac) if (1 - p1_frac) > 0 else float("inf")
p1_max_for_target = (r2 - (target_pct_black/100.0)*r2) / (r2 - r1) if (r2 - r1) != 0 else float("nan")

# ====== TOP CARDS ======
k1, k2, k3, k4 = st.columns(4)
k1.metric("Effective blended rate", fmt_rate(rate_eff))
k2.metric("MMK — With Split (net)", fmt_mmk(mmk_split))
k3.metric("MMK — Full Black (net)", fmt_mmk(mmk_black))
k4.metric("Shortfall vs Full Black", fmt_mmk(shortfall))

k5, k6, k7 = st.columns(3)
k5.metric("% of Black Achieved", f"{pct_of_black*100:,.2f}%" if not math.isnan(pct_of_black) else "—")
k6.metric("% Shortfall", f"{pct_shortfall*100:,.2f}%" if not math.isnan(pct_shortfall) else "—")
k7.metric("Per $100k Shortfall", fmt_mmk(100000*(r2 - rate_eff)))

st.markdown("---")

# ====== SIMPLE CHART ======
left, right = st.columns([1, 1])
with left:
    st.subheader("MMK Comparison (Net)")
    fig, ax = plt.subplots()
    ax.bar(["With Split (net)", "Full Black (net)"], [mmk_split, mmk_black])
    ax.set_ylabel("MMK")
    st.pyplot(fig)

with right:
    st.subheader("Per-$1 View")
    fig2, ax2 = plt.subplots()
    ax2.bar(["Actual (blended)", "Full Black"], [rate_eff, r2])
    ax2.set_ylabel("MMK per USD")
    st.pyplot(fig2)

st.markdown("---")

# ====== SENSITIVITY (tiny & intuitive) ======
st.subheader("Sensitivity — Quick Grid")
st.caption("Shortfall (MMK) for p₁ in rows, r₂ in columns. Fees cancel in comparison.")
p1_list = list(range(0, 55, 5))
r2_list = [r2 + step for step in [-400, -300, -200, -100, 0, 100, 200, 300, 400]]
grid = []
for p in p1_list:
    row = []
    for r2h in r2_list:
        # Shortfall ≈ USD * p1 * (r1 − r2h)
        row.append(usd * (p/100.0) * (r1 - r2h))
    grid.append(row)

df = pd.DataFrame(grid, index=[f"{p}%" for p in p1_list], columns=[f"{int(x)}" for x in r2_list])
st.dataframe(df.style.format("{:,.0f}"))

st.markdown("---")

# ====== STRATEGY HINTS ======
st.subheader("Strategy Hints")
c1, c2 = st.columns(2)
with c1:
    st.markdown(f"- **Max official p₁ to keep ≥ {target_pct_black}% of black**: "
                f"≈ **{p1_max_for_target:.2%}**" if not math.isnan(p1_max_for_target) else "- Not defined (r₂=r₁).")
    st.markdown(f"- **r₂ required to be fully whole at current p₁**: **{r2_needed_to_be_whole:,.2f} MMK/USD**" 
                if r2_needed_to_be_whole != float('inf') else "- r₂ required: ∞ (p₁=100%).")
with c2:
    st.markdown("- **Negotiation framing**: Offer at the **blended rate** or quote '% of black achieved'.")
    st.markdown("- **Pricing guardrails**: Use the max p₁ figure when discussing policy changes or contracts.")

st.markdown("---")

# ====== SCENARIOS ======
st.subheader("Save/Compare Scenarios")
with st.expander("Add scenarios (optional)"):
    sc_col = st.columns(4)
    sc_name = sc_col[0].text_input("Scenario name", value="Current Policy")
    sc_usd = sc_col[1].number_input("USD", min_value=0.0, value=usd, step=1000.0, format="%.2f")
    sc_p1  = sc_col[2].number_input("p₁ %", min_value=0.0, max_value=100.0, value=float(p1_pct), step=1.0, format="%.0f")
    sc_r1  = sc_col[3].number_input("r₁", min_value=0.0, value=r1, step=50.0, format="%.2f")
    sc_r2  = st.number_input("r₂", min_value=0.0, value=r2, step=50.0, format="%.2f")

    if 'scenarios' not in st.session_state:
        st.session_state['scenarios'] = []

    if st.button("➕ Add scenario"):
        st.session_state['scenarios'].append({
            "Name": sc_name,
            "USD": sc_usd,
            "p1%": sc_p1,
            "r1": sc_r1,
            "r2": sc_r2,
            "BlendedRate": blended_rate(sc_p1, sc_r1, sc_r2),
            "MMK_Split": mmk_with_split(sc_usd, sc_p1, sc_r1, sc_r2, fee_flat, fee_pct),
            "MMK_Black": mmk_full_black(sc_usd, sc_r2, fee_flat, fee_pct),
        })

    if st.session_state['scenarios']:
        df_sc = pd.DataFrame(st.session_state['scenarios'])
        df_sc["Shortfall"] = df_sc["MMK_Black"] - df_sc["MMK_Split"]
        st.dataframe(df_sc.style.format({
            "USD": "{:,.0f}",
            "p1%": "{:,.0f}",
            "r1": "{:,.0f}",
            "r2": "{:,.0f}",
            "BlendedRate": "{:,.2f}",
            "MMK_Split": "{:,.0f}",
            "MMK_Black": "{:,.0f}",
            "Shortfall": "{:,.0f}",
        }))
        st.download_button("Download scenarios CSV", df_sc.to_csv(index=False).encode("utf-8"), file_name="scenarios.csv", mime="text/csv")

st.caption("Tip: Share this app link with your dad and team. Use the sidebar to tweak numbers live.")
