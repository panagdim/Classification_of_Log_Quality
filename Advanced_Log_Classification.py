import pandas as pd
import tkinter as tk
from tkinter import filedialog

# -------------VERSION 1.3------------------------
# -------------Considering More Rules-------------

# 1. Classification Function

def classify_tree(row):
    height = row['Height_m']
    diameter = row['Diameter_cm']
    defect_type = row['Defect_Type']
    defect_count = row['Defect_Count']

    # If no defects at all, automatically High classification

    if defect_type == 'None' or defect_count == 0:
        return 'High'

    # Base quality from size (biometrics)
    
    if height > 25 and diameter > 40:
        quality = 3   # High
    elif height > 15 and diameter > 25:
        quality = 2   # Medium
    else:
        quality = 1   # Low


    # Adjust based on defect TYPE
   
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

    # Adjust based on defect COUNT
 
    # More defects = more penalty
    if defect_count == 0:
        count_penalty = 0
    elif defect_count <= 2:
        count_penalty = 1
    elif defect_count <= 5:
        count_penalty = 2
    else:
        count_penalty = 3

    # Final score

    final_score = quality - (penalty + count_penalty) * 0.5

    # Convert score to category
   
    if final_score >= 2.5:
        return 'High'
    elif final_score >= 1.5:
        return 'Medium'
    elif final_score >= 0.5:
        return 'Low'
    else:
        return 'Very Low'

# 2. Load Data

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

# 3. Apply Classification

data['Quality'] = data.apply(classify_tree, axis=1)

# 4. Save Results

# Passing example of full path
output_file = "C:/Users/Dimitris/Desktop/Classified_Logs.xlsx"
data.to_excel(output_file, index=False)

print(f"\n✅ Classification complete! Saved to: {output_file}")

# 5. Summary

print("\nQuality Summary:")
print(data['Quality'].value_counts())


