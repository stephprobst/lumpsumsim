import streamlit as st
import pandas as pd
from main import simulate_retirement_investable

st.title("Retirement Investable Capital Simulation")

st.sidebar.header("Simulation Parameters")

lump_sum = st.sidebar.number_input(
    "Lump Sum (€)",
    min_value=0.0,
    value=0.0,
    step=1000.0,
    format="%.2f"
)

pension = st.sidebar.number_input(
    "Yearly Pension (€)",
    min_value=0.0,
    value=12000.0,
    step=1000.0,
    format="%.2f"
)

current_age = st.sidebar.number_input(
    "Current Age",
    min_value=0,
    value=65,
    step=1
)

age_of_death = st.sidebar.number_input(
    "Age of Death",
    min_value=0,
    value=85,
    step=1
)

other_income_social = st.sidebar.number_input(
    "Other Income for Social Security (€)",
    min_value=0.0,
    value=70000.0,
    step=1000.0,
    format="%.2f"
)

other_income_tax = st.sidebar.number_input(
    "Other Income for Income Tax (€)",
    min_value=0.0,
    value=70000.0,
    step=1000.0,
    format="%.2f"
)

market_return_percentage = st.sidebar.number_input(
    "Annual Market Return (%)",
    min_value=0.0,
    value=3.0,
    step=0.1,
    format="%.2f"
)
market_return = market_return_percentage / 100  # convert to a fraction

if st.sidebar.button("Run Simulation"):
    if age_of_death <= current_age:
        st.error("Age of Death must be greater than Current Age.")
    else:
        results = simulate_retirement_investable(
            lump_sum=lump_sum,
            pension=pension,
            current_age=current_age,
            age_of_death=age_of_death,
            other_income_social=other_income_social,
            other_income_tax=other_income_tax,
            market_return=market_return
        )
        df = pd.DataFrame(results)
        st.write("### Simulation Results")
        st.dataframe(df)
