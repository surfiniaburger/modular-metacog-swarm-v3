import csv

tiers = {}
with open('./kaggle_notebooks/mcsb_master_v3.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        t = row['tier']
        tiers[t] = tiers.get(t, 0) + 1

print(tiers)
