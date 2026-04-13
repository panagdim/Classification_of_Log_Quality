import pandas as pd
import math
from tkinter import Tk, filedialog
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font
from openpyxl.formatting.rule import FormulaRule

# -------------------------
# FILE DIALOG
# -------------------------
def select_file():
    root = Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )


# -------------------------
# SAFE BOOLEAN
# -------------------------
def to_bool(val):
    return str(val).strip().lower() in ["true", "1", "yes"]


# -------------------------
# CLAMP VALUES
# -------------------------
def clamp(value, min_val, max_val):
    return max(min_val, min(max_val, value))


# -------------------------
# VOLUME (m³)
# -------------------------
def calculate_volume(length, diameter_cm):
    diameter_m = diameter_cm / 100
    radius = diameter_m / 2
    return round(math.pi * radius**2 * length, 4)


# -------------------------
# FIX DATA LOGIC
# -------------------------
def fix_defects(df):

    # Knots
    df["Count_Knots"] = df.apply(
        lambda r: max(1, int(r["Count_Knots"])) if r["Has_Knots"] else 0,
        axis=1
    )

    # Cracks
    df["Count_Cracks"] = df.apply(
        lambda r: max(1, int(r["Count_Cracks"])) if r["Has_Cracks"] else 0,
        axis=1
    )

    return df


# -------------------------
# EVALUATION MODEL
# -------------------------
def evaluate_log(length, diameter, knots, cracks,
                 has_forking, has_bend, has_disease):

    # -------------------------
    # PERFECT LOG OVERRIDE
    # -------------------------
    no_defects = (
        knots == 0 and cracks == 0 and
        not has_forking and not has_bend and not has_disease
    )

    if no_defects and length >= 7 and diameter >= 80:
        return 95, "High"

    # -------------------------
    # SIZE SCORE
    # -------------------------
    length_score = 45 * (1 - math.exp(-0.4 * (length - 2)))
    diameter_score = 45 * (diameter / 150) ** 0.85
    size_score = length_score + diameter_score

    # -------------------------
    # DEFECT PENALTIES
    # -------------------------
    knot_penalty = knots * 1.8
    crack_penalty = cracks * (2.2 + 0.25 * length)

    fork_penalty = 8 if has_forking else 0
    bend_penalty = 6 if has_bend else 0
    disease_penalty = 12 if has_disease else 0

    defect_penalty = (
        knot_penalty +
        crack_penalty +
        fork_penalty +
        bend_penalty +
        disease_penalty
    )

    # -------------------------
    # INTERACTIONS
    # -------------------------
    interaction_penalty = 0

    if cracks > 0 and has_disease:
        interaction_penalty += 6

    if knots > 5 and cracks > 3:
        interaction_penalty += 5

    if length > 7 and has_bend:
        interaction_penalty += 4

    if has_forking:
        interaction_penalty += length * 0.4

    # -------------------------
    # FINAL SCORE
    # -------------------------
    score = size_score - defect_penalty - interaction_penalty

    # Bonus for clean logs
    if no_defects:
        score += 10

    score = max(0, min(100, score))

    # -------------------------
    # CATEGORY
    # -------------------------
    if score >= 80:
        quality = "High"
    elif score >= 60:
        quality = "Medium"
    elif score >= 40:
        quality = "Low"
    else:
        quality = "Very Low"

    return round(score, 2), quality


# -------------------------
# MAIN PIPELINE
# -------------------------
file_path = select_file()

if not file_path:
    print("❌ No file selected")
    exit()

df = pd.read_excel(file_path)

# -------------------------
# CLEAN DATA TYPES
# -------------------------
df["Has_Knots"] = df["Has_Knots"].apply(to_bool)
df["Has_Cracks"] = df["Has_Cracks"].apply(to_bool)
df["Has_Forking"] = df["Has_Forking"].apply(to_bool)
df["Has_Bend"] = df["Has_Bend"].apply(to_bool)
df["Has_Disease"] = df["Has_Disease"].apply(to_bool)

df["Count_Knots"] = df["Count_Knots"].fillna(0)
df["Count_Cracks"] = df["Count_Cracks"].fillna(0)

# -------------------------
# FIX LOGIC ISSUES
# -------------------------
df = fix_defects(df)

# -------------------------
# PROCESS
# -------------------------
scores = []
qualities = []
volumes = []

for _, row in df.iterrows():

    # enforce realistic bounds
    length = clamp(row["Length_m"], 2, 10)
    diameter = clamp(row["Diameter_cm"], 10, 150)

    knots = int(row["Count_Knots"])
    cracks = int(row["Count_Cracks"])

    volume = calculate_volume(length, diameter)

    score, quality = evaluate_log(
        length, diameter, knots, cracks,
        row["Has_Forking"],
        row["Has_Bend"],
        row["Has_Disease"]
    )

    scores.append(score)
    qualities.append(quality)
    volumes.append(volume)

# -------------------------
# OUTPUT
# -------------------------
df["Length_m"] = df["Length_m"].clip(2, 10)
df["Diameter_cm"] = df["Diameter_cm"].clip(10, 150)

df["Volume_m3"] = volumes
df["Score"] = scores
df["Quality"] = qualities


# Save first using pandas

output_path = "C:/Users/Dimitris/Desktop/classified_logs.xlsx"
df.to_excel(output_path, index=False)

# -------------------------
# OPEN WITH OPENPYXL
# -------------------------
wb = load_workbook(output_path)
ws = wb.active

# -------------------------
# AUTO COLUMN WIDTH
# -------------------------
for col in ws.columns:
    max_length = 0
    col_letter = col[0].column_letter

    for cell in col:
        try:
            if cell.value:
                max_length = max(max_length, len(str(cell.value)))
        except:
            pass

    ws.column_dimensions[col_letter].width = max_length + 2


# -------------------------
# CONDITIONAL FORMATTING
# -------------------------
green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
yellow_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
orange_fill = PatternFill(start_color="F4B084", end_color="F4B084", fill_type="solid")
red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

# Find Score column letter
score_col = None
quality_col = None

for cell in ws[1]:
    if cell.value == "Score":
        score_col = cell.column_letter
    if cell.value == "Quality":
        quality_col = cell.column_letter


# Apply rules on Quality column
ws.conditional_formatting.add(
    f"{quality_col}2:{quality_col}{ws.max_row}",
    FormulaRule(formula=[f'${quality_col}2="High"'], fill=green_fill)
)

ws.conditional_formatting.add(
    f"{quality_col}2:{quality_col}{ws.max_row}",
    FormulaRule(formula=[f'${quality_col}2="Medium"'], fill=yellow_fill)
)

ws.conditional_formatting.add(
    f"{quality_col}2:{quality_col}{ws.max_row}",
    FormulaRule(formula=[f'${quality_col}2="Low"'], fill=orange_fill)
)

ws.conditional_formatting.add(
    f"{quality_col}2:{quality_col}{ws.max_row}",
    FormulaRule(formula=[f'${quality_col}2="Very Low"'], fill=red_fill)
)

# -------------------------
# SAVE FINAL FILE
# -------------------------
wb.save(output_path)

print("🎨 Excel formatting applied!")
print(f"📁 Final file ready: {output_path}")
print("✅ Evaluation complete!")
