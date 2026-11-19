# FreshFlow Juice Company - NumPy Data Analyst

import csv
import random
from pathlib import Path
import numpy as np

random.seed(10)
BASE = Path(__file__).parent
DATA = BASE / "freshflow_sales_5000.csv"
OUT = BASE / "outputs_5000"
OUT.mkdir(exist_ok=True)

products = ["Orange Juice", "Mango Juice", "Apple Juice", "Mixed Juice"]
outlets = ["North", "South", "East", "West"]
prices = [80, 100, 90, 120]

# Generate exactly 5,000 sample sales records
with DATA.open("w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["ID", "Day", "Product", "Outlet", "Quantity", "Price", "Discount"])
    for i in range(1, 5001):
        p = random.randrange(4)
        w.writerow([i, random.randint(1, 30), products[p],
                    random.choice(outlets), random.randint(1, 10),
                    prices[p], random.choice([0, 0.05, 0.10, 0.15])])

# Read CSV
with DATA.open() as f:
    rows = list(csv.DictReader(f))

# Convert data to NumPy arrays
ids = np.array([int(r["ID"]) for r in rows])
days = np.array([int(r["Day"]) for r in rows])
quantity = np.array([int(r["Quantity"]) for r in rows])
price = np.array([float(r["Price"]) for r in rows])
discount = np.array([float(r["Discount"]) for r in rows])
product = np.array([r["Product"] for r in rows])
outlet = np.array([r["Outlet"] for r in rows])

# Data cleaning: remove invalid records
valid = ((days >= 1) & (days <= 30) & (quantity > 0) &
         (price > 0) & (discount >= 0) & (discount <= 1))
ids, days, quantity = ids[valid], days[valid], quantity[valid]
price, discount = price[valid], discount[valid]
product, outlet = product[valid], outlet[valid]

# Calculate sales
gross = quantity * price
net = gross * (1 - discount)
cost = net * 0.55                 # Assumption: cost is 55% of net sales
profit = net - cost

# Overall business summary
summary = [
    ["Total Transactions", len(ids)],
    ["Total Quantity Sold", int(quantity.sum())],
    ["Gross Sales", round(gross.sum(), 2)],
    ["Net Sales", round(net.sum(), 2)],
    ["Total Profit", round(profit.sum(), 2)],
    ["Average Order Value", round(net.mean(), 2)]
]

# Product-wise performance
product_report = [["Product", "Quantity", "Net Sales", "Profit"]]
for name in products:
    m = product == name
    product_report.append([name, int(quantity[m].sum()),
                           round(net[m].sum(), 2), round(profit[m].sum(), 2)])

# Outlet-wise performance
outlet_report = [["Outlet", "Transactions", "Net Sales"]]
for name in outlets:
    m = outlet == name
    outlet_report.append([name, int(m.sum()), round(net[m].sum(), 2)])

# Daily sales trend
daily_report = [["Day", "Net Sales"]]
for day in range(1, 31):
    daily_report.append([day, round(net[days == day].sum(), 2)])

# Save reports as CSV files
def save_csv(filename, data):
    with (OUT / filename).open("w", newline="") as f:
        csv.writer(f).writerows(data)

save_csv("business_summary.csv", summary)
save_csv("product_performance.csv", product_report)
save_csv("outlet_performance.csv", outlet_report)
save_csv("daily_sales_trend.csv", daily_report)

# Basic validation checks
checks = {
    "No invalid quantities": bool(np.all(quantity > 0)),
    "Discounts between 0 and 1": bool(np.all((discount >= 0) & (discount <= 1))),
    "Sales are not negative": bool(np.all(net >= 0)),
    "Transaction IDs are unique": len(np.unique(ids)) == len(ids)
}
with (OUT / "validation_tests.txt").open("w") as f:
    for name, result in checks.items():
        f.write(f"{name}: {'PASS' if result else 'FAIL'}\n")

print("FRESHFLOW JUICE COMPANY - NUMPY DATA ANALYST")
print("--------------------------------------------")
print("Total records loaded:", len(rows))
print("Valid records:", len(ids))
print("Rejected records:", len(rows) - len(ids))
print("Net sales:", round(net.sum(), 2))
print("Total profit:", round(profit.sum(), 2))
print("Validation:", "ALL PASS" if all(checks.values()) else "CHECK FAILED")
print("Reports saved in:", OUT)
