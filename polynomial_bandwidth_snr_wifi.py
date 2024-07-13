import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Polynomial degree
deg = 5

# Data points
snr_20MHz = np.array([2, 5, 9, 11, 15, 18, 20, 25, 29])
data_rate_20MHz = np.array([7.2, 14.4, 21.7, 28.9, 43.3, 57.8, 65, 72.2, 86.7])

snr_40MHz = np.array([5, 8, 12, 14, 18, 21, 23, 28, 32, 34])
data_rate_40MHz = np.array([15, 30, 45, 60, 90, 120, 135, 150, 180, 200])

snr_80MHz = np.array([8, 11, 15, 17, 21, 24, 26, 31, 35, 37])
data_rate_80MHz = np.array([32.5, 65, 97.5, 130, 195, 260, 292.5, 325, 390, 433.4])

# Combine all data points
snr = np.concatenate((snr_20MHz, snr_40MHz, snr_80MHz))
bandwidth = np.concatenate((np.full_like(snr_20MHz, 20), np.full_like(snr_40MHz, 40), np.full_like(snr_80MHz, 80)))
data_rate = np.concatenate((data_rate_20MHz, data_rate_40MHz, data_rate_80MHz))

# Create feature matrix
X = np.column_stack((bandwidth, snr))

# Create polynomial features
poly = PolynomialFeatures(degree=deg)
X_poly = poly.fit_transform(X)

# Fit polynomial regression
model = LinearRegression()
model.fit(X_poly, data_rate)

# Get coefficients
coeffs = model.coef_
intercept = model.intercept_

# Calculate predictions
y_pred = model.predict(X_poly)

# Calculate error statistics
mae = mean_absolute_error(data_rate, y_pred)
rmse = np.sqrt(mean_squared_error(data_rate, y_pred))
mape = np.mean(np.abs((data_rate - y_pred) / data_rate)) * 100

errors = y_pred - data_rate
absolute_errors = np.abs(errors)
relative_errors = absolute_errors / data_rate * 100

print("\nError Statistics:")
print(f"Mean Error: {np.mean(errors):.2f}")
print(f"Mean Absolute Error: {mae:.2f}")
print(f"Root Mean Squared Error: {rmse:.2f}")
print(f"Mean Absolute Percentage Error: {mape:.2f}%")
print(f"Lowest Error: {np.min(absolute_errors):.2f}")
print(f"Highest Error: {np.max(absolute_errors):.2f}")
print(f"Lowest Relative Error: {np.min(relative_errors):.2f}%")
print(f"Highest Relative Error: {np.max(relative_errors):.2f}%")
print(f"Standard Deviation of Errors: {np.std(errors):.2f}")
print(f"Median Absolute Error: {np.median(absolute_errors):.2f}")

# R-squared score
r2 = model.score(X_poly, data_rate)
print(f"R-squared Score: {r2:.4f}")





formula_sci = f"={intercept:.7e}"
for i, coef in enumerate(coeffs[1:]):
    powers = poly.powers_[i+1]
    term = f"{coef:.7e}"
    if powers[0] > 1:
        term += f"*BW^{powers[0]}"
    elif powers[0] == 1:
        term += f"*BW"
    if powers[1] > 1:
        term += f"*SNR^{powers[1]}"
    elif powers[1] == 1:
        term += f"*SNR"
    formula_sci += f"+{term}"

# Replace instances of "+-" with "-" to clean up the formula
formula_sci = formula_sci.replace("+-", "-")

print("\nFormula sci:")
print(formula_sci)


# For spreadsheets
spreadsheet_formula_sci = f"={intercept:.7e}"
for i, coef in enumerate(coeffs[1:]):
    powers = poly.powers_[i+1]
    term = f"{coef:.7e}"
    if powers[0] > 1:
        term += f"*POWER(A2,{powers[0]})"
    elif powers[0] == 1:
        term += f"*A2"
    if powers[1] > 1:
        term += f"*POWER(B2,{powers[1]})"
    elif powers[1] == 1:
        term += f"*B2"
    spreadsheet_formula_sci += f"+{term}"

spreadsheet_formula_sci = spreadsheet_formula_sci.replace("+-", "-")

print("\nSpreadsheet formula:")
print(spreadsheet_formula_sci)



# Polynomial formula
def polynomial_formula(BW, SNR_dB):
    formula = f"{intercept:.7e}"
    for i, coef in enumerate(coeffs[1:]):
        powers = poly.powers_[i+1]
        term = f"{coef:.7e}"
        if powers[0] > 1:
            term += f"*BW**{powers[0]}"
        elif powers[0] == 1:
            term += f"*BW"
        if powers[1] > 1:
            term += f"*SNR_dB**{powers[1]}"
        elif powers[1] == 1:
            term += f"*SNR_dB"
        formula += f"+{term}"
    
    # Replace instances of "+-" with "-" to clean up the formula
    formula = formula.replace("+-", "-")
    return formula
print("\nPolynomial formula python function:")
print(f"def polynomial_formula(BW, SNR_dB):\n    return ( {polynomial_formula('BW', 'SNR_dB')} )")
