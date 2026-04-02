# %%
import pandas as pd
import tkinter as tk
from tkinter import filedialog

# -----------------------------
# 1. Define classification rules based on height, diameter, and defects (categorical)
# -----------------------------
def classify_tree(row):
    height = row['Height_m']
    diameter = row['Diameter_cm']
    defect = row['Defects']
    
    # Example rules combining numeric and categorical features
    if height > 20 and diameter > 35 and defect == 'None':
        return 'High'
    elif height >= 15 and diameter >= 25 and defect in ['None', 'Knots']:
        return 'Medium'
    elif defect in ['Cracks', 'Forking']:
        return 'Low'
    elif defect == 'Diseases':
        return 'Very Low'
    else:
        return 'Low'  # default catch-all

# -----------------------------
# 2. Load data from file
# -----------------------------
# Pick the file ONLY .txt

# Hide the root window
root = tk.Tk()
root.withdraw()

# Open file dialog
file_path = filedialog.askopenfilename(
    title="Select your file",
    filetypes=[("Text files", "*.txt"), ("Excel files", "*.xlsx")]
)

print(file_path)

if file_path.endswith('.csv') or file_path.endswith('.txt'):
    data = pd.read_csv(file_path)
elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
    data = pd.read_excel(file_path)
else:
    raise ValueError("Unsupported file type! Please use CSV, TXT, or Excel.")

# -----------------------------
# 3. Apply classification
# -----------------------------
data['Quality'] = data.apply(classify_tree, axis=1)

# -----------------------------
# 4. Save results
# -----------------------------
output_file = "C:/Users/Dimitris/Desktop/classified_trees_with_defect_count_output.xlsx"
data.to_excel(output_file, index=False)
print(f"Classification complete! Results saved to {output_file}")

# -----------------------------
# 5. Optional summary
# -----------------------------
print("\nTree Quality Summary:")
print(data['Quality'].value_counts())

# %%
import pandas as pd
import tkinter as tk
from tkinter import filedialog

# -----------------------------
# 1. Define your classification rules based on height, diameter, and defects (numerical)
# -----------------------------
def classify_tree(row):
    height = row['Height_m']
    diameter = row['Diameter_cm']
    defects = row['Defects']
    
    # Example rules (customize as needed)
    if height > 20 and diameter > 35 and defects == 0:
        return 'High'
    elif height >= 15 and diameter >= 25 and defects <= 2:
        return 'Medium'
    else:
        return 'Low'

# -----------------------------
# 2. Load data from file
# -----------------------------

# Hide the root window
root = tk.Tk()
root.withdraw()

# Open file dialog
file_path = filedialog.askopenfilename(
    title="Select your file",
    filetypes=[("Text files", "*.txt"), ("Excel files", "*.xlsx")]
)

print(file_path)

# Detect file type and read
if file_path.endswith('.csv') or file_path.endswith('.txt'):
    data = pd.read_csv(file_path)
elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
    data = pd.read_excel(file_path)
else:
    raise ValueError("Unsupported file type! Please use CSV, TXT, or Excel.")

# -----------------------------

# 3. Apply classification
# -----------------------------
data['Quality'] = data.apply(classify_tree, axis=1)

# -----------------------------
# 4. Save results
# -----------------------------
output_file = "C:/Users/Dimitris/Desktop/classified_trees_with_defect_numerical_output.xlsx"
data.to_excel(output_file, index=False)
print(f"Classification complete! Results saved to {output_file}")

# -----------------------------
# 5. Optional: Print a summary
# -----------------------------
print("\nTree Quality Summary:")
print(data['Quality'].value_counts())


# %%
import pandas as pd
import tkinter as tk
from tkinter import filedialog

# Advanced Version Considering More Rules

# -----------------------------
# 1. Classification Function
# -----------------------------
def classify_tree(row):
    height = row['Height_m']
    diameter = row['Diameter_cm']
    defect_type = row['Defect_Type']
    defect_count = row['Defect_Count']

# -----------------------------
    # If no defects at all, automatically High classification
    # -----------------------------
    if defect_type == 'None' or defect_count == 0:
        return 'High'

    # -----------------------------
    # Base quality from size (biometrics)
    # -----------------------------
    if height > 25 and diameter > 40:
        quality = 3   # High
    elif height > 15 and diameter > 25:
        quality = 2   # Medium
    else:
        quality = 1   # Low

    # -----------------------------
    # Adjust based on defect TYPE
    # -----------------------------
    if defect_type == 'None':
        penalty = 0
    elif defect_type == 'Knots':
        penalty = 1
    elif defect_type == 'Cracks':
        penalty = 2
    elif defect_type == 'Forking':
        penalty = 2
    elif defect_type == 'Diseases':
        penalty = 3
    else:
        penalty = 2

    # -----------------------------
    # Adjust based on defect COUNT
    # -----------------------------
    # More defects = more penalty
    if defect_count == 0:
        count_penalty = 0
    elif defect_count <= 2:
        count_penalty = 1
    elif defect_count <= 5:
        count_penalty = 2
    else:
        count_penalty = 3

    # -----------------------------
    # Final score
    # -----------------------------
    final_score = quality - (penalty + count_penalty) * 0.5

    # -----------------------------
    # Convert score to category
    # -----------------------------
    if final_score >= 2.5:
        return 'High'
    elif final_score >= 1.5:
        return 'Medium'
    elif final_score >= 0.5:
        return 'Low'
    else:
        return 'Very Low'


# -----------------------------
# 2. Load Data
# -----------------------------

# Hide the root window
root = tk.Tk()
root.withdraw()

# Open file dialog
file_path = filedialog.askopenfilename(
    title="Select your file",
    filetypes=[("Text files", "*.txt"), ("Excel files", "*.xlsx")]
)

print(file_path)

if file_path.endswith('.csv') or file_path.endswith('.txt'):
    data = pd.read_csv(file_path)
elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
    data = pd.read_excel(file_path)
else:
    raise ValueError("Unsupported file type!")

# -----------------------------
# 3. Apply Classification
# -----------------------------
data['Quality'] = data.apply(classify_tree, axis=1)

# -----------------------------
# 4. Save Results
# -----------------------------
output_file = "C:/Users/Dimitris/Desktop/classified_logs.xlsx"
data.to_excel(output_file, index=False)

print(f"\n✅ Classification complete! Saved to: {output_file}")

# -----------------------------
# 5. Summary
# -----------------------------
print("\nQuality Summary:")
print(data['Quality'].value_counts())


