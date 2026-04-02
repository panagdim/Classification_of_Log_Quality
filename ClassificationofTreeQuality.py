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


