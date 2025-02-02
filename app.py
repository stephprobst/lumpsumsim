import streamlit as st
import pandas as pd
from main import simulate_retirement_investable

st.title("Retirement Investable Capital Simulation")

st.markdown(
    """
    This simulation models the accumulation of investable capital from a lump sum and a pension.
    
    **Parameter Explanations:**
    - **Lump Sum (€):** A one-time payment received at retirement.
    - **Yearly Pension (€):** Annual pension received. Its tax and social security effects are computed.
    - **Current Age:** Age at the start of the simulation.
    - **Age of Death:** Age until which the simulation runs.
    - **Other Income for Social Security (€):** Annual income used for calculating social security contributions.
    - **Other Income for Income Tax (€):** Annual income used for computing income tax.
    
      > **Important:** The Social Security and Income Tax income figures are **not additive**. They are separate bases used in calculating social security contributions and income tax, respectively.
    
    - **Annual Market Return (%):** Expected annual rate of return on invested capital.
    """
)

st.sidebar.header("Simulation Parameters")

lump_sum = st.sidebar.number_input(
    "Lump Sum (€)",
    min_value=0.0,
    value=0.0,
    step=1000.0,
    format="%.2f",
    help="One-time payment received at retirement."
)

pension = st.sidebar.number_input(
    "Yearly Pension (€)",
    min_value=0.0,
    value=12000.0,
    step=1000.0,
    format="%.2f",
    help="Annual pension received, with tax and social security applied."
)

current_age = st.sidebar.number_input(
    "Current Age",
    min_value=0,
    value=65,
    step=1,
    help="Age at the start of the simulation."
)

age_of_death = st.sidebar.number_input(
    "Age of Death",
    min_value=0,
    value=85,
    step=1,
    help="Age until which the simulation runs."
)

other_income_social = st.sidebar.number_input(
    "Other Income for Social Security (€)",
    min_value=0.0,
    value=70000.0,
    step=1000.0,
    format="%.2f",
    help="Income used to calculate social security contributions."
)

other_income_tax = st.sidebar.number_input(
    "Other Income for Income Tax (€)",
    min_value=0.0,
    value=70000.0,
    step=1000.0,
    format="%.2f",
    help="Income used to compute income tax (separate from the social security base)."
)

market_return_percentage = st.sidebar.number_input(
    "Annual Market Return (%)",
    min_value=0.0,
    value=3.0,
    step=0.1,
    format="%.2f",
    help="Expected annual return rate on the invested capital (in %)."
)
market_return = market_return_percentage / 100  # Convert percentage to fraction

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
