#!/usr/bin/env python3
"""
Simulation of investable capital built only from a lump sum and a pension—
excluding the other incomes from the aggregated (investable) capital.
The other incomes (one relevant for both income tax and social security,
and one only relevant for income tax) are still used to determine the marginal
tax and social security rates.

This version now also deducts a 25% capital gains tax plus the solidarity surcharge
(on the market returns) and prints the output table with fixed-width columns.

Assumptions:
  - German income tax (simplified progressive model) with the "Fünftelregelung"
    for lump sum taxation.
  - Social security contributions are computed on income up to a set threshold,
    with the lump sum social security liability spread evenly over 10 years.
  - Only the net effects of the lump sum and pension (after tax and social security)
    are added to the investable capital.
  - Annual market returns are subject to a capital gains tax at an effective rate.
  - 0% inflation.
  
Output: A table with fixed-width columns showing:
  - Calendar Year, Age, Capital at Start, Lump Sum Gross, Lump Sum Tax,
    Lump Sum SS, Pension Gross, Pension Tax, Pension SS, Net Flow,
    Gross Investment Return, Investment Tax, Net Investment Return, Capital End
"""

# ----- CONFIGURATION CONSTANTS -----
START_YEAR = 2025

# Example social security constants (values in € and rates as examples)
SOCIAL_SECURITY_RATE = 0.186        # 20% (example)
SOCIAL_SECURITY_THRESHOLD = 66150  # Upper income threshold for social security contributions

# Capital gains tax:
# 25% flat tax plus a solidarity surcharge of 5.5% on the tax amount.
# Effective rate = 25% * (1 + 0.055) ≈ 26.38%
CAPITAL_GAINS_TAX_RATE = 0.2638

# ----- TAX FUNCTIONS (Simplified Examples) -----
def german_income_tax(income):
    """
    Calculate German income tax using official formulas from §32a EStG.
    (Coefficients here are those for 2020; adjust thresholds/coefs for 2025 if available.)
    
    - No tax for income up to 9,744€
    - For income between 9,745€ and 14,753€:
         y = (income - 9,744) / 10,000
         tax = (995.21 * y + 1400) * y
    - For income between 14,754€ and 57,918€:
         z = (income - 14,753) / 10,000
         tax = (208.85 * z + 2397) * z + 950.96
    - For income between 57,919€ and 274,612€:
         tax = 0.42 * income - 9,136.63
    - For income above 274,612€:
         tax = 0.45 * income - 17,374.99
    """
    if income <= 11784:
        return 0.0
    elif income <= 17005:
        y = (income - 11784) / 10000.0
        return (954.8 * y + 1400) * y
    elif income <= 66760:
        z = (income - 17005) / 10000.0
        return (181.19 * z + 2397) * z + 991.21
    elif income <= 277825:
        return 0.42 * income - 10636.31
    else:
        return 0.45 * income - 18971.06

def lump_sum_tax_fünftel(lump_sum, base_income):
    """
    Calculate the lump sum tax using the Fünftelregelung.
    The lump sum is divided into 5 equal parts. The tax on one-fifth of the lump sum,
    when added to the base income, is computed. The incremental tax (difference) is
    multiplied by 5.
    """
    base_tax = german_income_tax(base_income)
    tax_with_fraction = german_income_tax(base_income + lump_sum / 5)
    return 5 * (tax_with_fraction - base_tax)

# ----- SIMULATION FUNCTION (Investable Capital Only) -----
def simulate_retirement_investable(
    lump_sum: float,
    pension: float,
    current_age: int,
    age_of_death: int,
    other_income_social: float,
    other_income_tax: float,
    market_return: float
):
    """
    Simulate year-by-year accumulation of investable capital where only the lump sum and pension
    (net of taxes and social security) are invested. Other incomes affect the marginal tax rates
    but are excluded from the investable capital.
    
    Now, the annual market returns are taxed at the effective capital gains tax rate.
    """
    num_years = age_of_death - current_age
    capital = 0.0  # Starting investable capital
    
    # Define the base incomes from the "other" sources.
    base_regular = other_income_tax + other_income_social  # for income tax
    base_ss = other_income_social  # for social security
    
    # --- Pension Calculations (These are constant every year) ---
    # Incremental income tax due to pension:
    pension_tax = german_income_tax(base_regular + pension) - german_income_tax(base_regular)
    # Incremental social security for pension:
    pension_ss = (min(base_ss + pension, SOCIAL_SECURITY_THRESHOLD) -
                  min(base_ss, SOCIAL_SECURITY_THRESHOLD)) * SOCIAL_SECURITY_RATE
    net_pension = pension - (pension_tax + pension_ss)
    
    # --- Lump Sum Calculations (Only in year 0) ---
    # For tax, the lump sum is added on top of base_regular + pension.
    lump_tax = lump_sum_tax_fünftel(lump_sum, base_regular + pension)
    net_lump = lump_sum - lump_tax
    # For social security, the lump sum is "spread" over 10 years.
    lump_share = lump_sum / 10  # each year's notional addition for social security purposes
    lump_ss_year = (min(base_ss + pension + lump_share, SOCIAL_SECURITY_THRESHOLD) -
                    min(base_ss + pension, SOCIAL_SECURITY_THRESHOLD)) * SOCIAL_SECURITY_RATE

    results = []
    for year_index in range(num_years):
        cal_year = START_YEAR + year_index
        age = current_age + year_index
        capital_start = capital

        # Determine cash flows for this year:
        if year_index == 0:
            # Year 0: both lump sum (gross and its tax are realized) and pension.
            lump_sum_gross = lump_sum
            lump_sum_tax = lump_tax
            # Lump sum SS is paid over 10 years (first year payment):
            lump_sum_ss = lump_ss_year
            pension_gross = pension
            pension_tax_value = pension_tax
            pension_ss_value = pension_ss
            # Net cash flow: net lump (after tax) plus net pension, then pay this year's lump SS.
            net_flow = net_lump + net_pension - lump_sum_ss
        elif year_index < 10:
            # Years 1 to 9: Only the pension is received investably,
            # but the lump sum's social security payment continues.
            lump_sum_gross = 0.0
            lump_sum_tax = 0.0
            lump_sum_ss = lump_ss_year
            pension_gross = pension
            pension_tax_value = pension_tax
            pension_ss_value = pension_ss
            net_flow = net_pension - lump_sum_ss
        else:
            # From year 10 onward, only pension flows.
            lump_sum_gross = 0.0
            lump_sum_tax = 0.0
            lump_sum_ss = 0.0
            pension_gross = pension
            pension_tax_value = pension_tax
            pension_ss_value = pension_ss
            net_flow = net_pension

        # --- Investment Return Calculation ---
        # First, add the net cash flow to the existing capital.
        new_basis = capital_start + net_flow
        # Compute gross investment return.
        gross_investment_return = new_basis * market_return
        # Compute capital gains tax on the investment return.
        investment_tax = gross_investment_return * CAPITAL_GAINS_TAX_RATE
        # Net investment return after tax.
        net_investment_return = gross_investment_return - investment_tax

        # Update capital at end of year.
        post_investment = new_basis + net_investment_return

        results.append({
            "Calendar Year": cal_year,
            "Age": age,
            "Capital Start": round(capital_start, 2),
            "Lump Sum Gross": round(lump_sum_gross, 2),
            "Lump Sum Tax": round(lump_sum_tax, 2),
            "Lump Sum SS": round(lump_sum_ss, 2),
            "Pension Gross": round(pension_gross, 2),
            "Pension Tax": round(pension_tax_value, 2),
            "Pension SS": round(pension_ss_value, 2),
            "Net Flow": round(net_flow, 2),
            "Gross Investment Return": round(gross_investment_return, 2),
            "Investment Tax": round(investment_tax, 2),
            "Net Investment Return": round(net_investment_return, 2),
            "Capital End": round(post_investment, 2)
        })

        # Update capital for next year:
        capital = post_investment

    return results

# ----- EXAMPLE USAGE -----
if __name__ == "__main__":
    # Example input parameters (adjust these as needed):
    lump_sum = 0         # one-time lump sum (in €)
    pension = 12000           # yearly pension (in €)
    current_age = 65
    age_of_death = 85
    other_income_social = 70000  # yearly income relevant for social security (in €)
    other_income_tax = 70000     # yearly income only relevant for income tax (in €)
    market_return = 0.03         # 3% annual market return
    
    sim_results = simulate_retirement_investable(
        lump_sum,
        pension,
        current_age,
        age_of_death,
        other_income_social,
        other_income_tax,
        market_return
    )
    
    # Define header for output:
    header = [
        "Calendar Year", "Age", "Capital Start", "Lump Sum Gross", "Lump Sum Tax",
        "Lump Sum SS", "Pension Gross", "Pension Tax", "Pension SS", "Net Flow",
        "Gross Investment Return", "Investment Tax", "Net Investment Return", "Capital End"
    ]
    
    # Set a fixed column width (adjust as needed)
    col_width = 24

    # Print header row with fixed-width columns:
    header_line = "".join(f"{col:<{col_width}}" for col in header)
    print(header_line)
    print("-" * len(header_line))
    
    # Print each row with fixed-width columns:
    for row in sim_results:
        row_line = "".join(f"{str(row[col]):<{col_width}}" for col in header)
        print(row_line)
