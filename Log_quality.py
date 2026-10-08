# Optimized GUI 
import re
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# ============================================================
# APPLICATION SETTINGS
# ============================================================

APP_TITLE = "Log Quality Evaluation"


# ============================================================
# SCORING LIMITS
# ============================================================

MIN_LOG_LENGTH_M = 1.5
MAX_LOG_LENGTH_M = 6.0

MIN_LOG_DIAMETER_CM = 15.0
MAX_LOG_DIAMETER_CM = 80.0


# ============================================================
# DATA PLAUSIBILITY LIMITS
# ============================================================

MIN_PLAUSIBLE_LOG_LENGTH_M = 0.5
MAX_PLAUSIBLE_LOG_LENGTH_M = 8.0
STRONG_TEST_LENGTH_M = 15.0

MIN_PLAUSIBLE_DIAMETER_CM = 5.0
MAX_PLAUSIBLE_DIAMETER_CM = 150.0
STRONG_TEST_DIAMETER_CM = 200.0

MIN_PLAUSIBLE_AGE_YEARS = 1.0
MAX_PLAUSIBLE_AGE_YEARS = 300.0
STRONG_TEST_AGE_YEARS = 500.0

MAX_PLAUSIBLE_KNOT_COUNT = 100
MAX_PLAUSIBLE_CRACK_COUNT = 100

MAX_PLAUSIBLE_KNOT_DIAMETER_MM = 500.0
MAX_PLAUSIBLE_CRACK_LENGTH_CM = 1000.0
MAX_PLAUSIBLE_CRACK_WIDTH_MM = 100.0

DUPLICATE_ROW_WARNING_RATIO = 0.20


# ============================================================
# EXCEL / OPENPYXL SAFETY
# ============================================================

# Excel cells cannot safely contain arbitrary control characters.
# This regex removes characters that openpyxl rejects.
ILLEGAL_EXCEL_CHARS_RE = re.compile(
    r"[\x00-\x08\x0B\x0C\x0E-\x1F]"
)

# Excel has a maximum cell text length of 32,767 characters.
MAX_EXCEL_CELL_LENGTH = 32767


def clean_excel_value(value):
    """
    Convert a value into something safely writable by openpyxl.

    This is important for the Calibration_Audit and Row_Audit sheets,
    where warning text can potentially become very long.
    """

    if value is None:
        return None

    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime()

    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return None

    if isinstance(value, (list, tuple, set)):
        value = " | ".join(
            str(x) for x in value
        )

    if isinstance(value, dict):
        value = str(value)

    if isinstance(value, str):

        value = ILLEGAL_EXCEL_CHARS_RE.sub(
            "",
            value
        )

        if len(value) > MAX_EXCEL_CELL_LENGTH:
            value = (
                value[:MAX_EXCEL_CELL_LENGTH - 30]
                + " ... [TRUNCATED]"
            )

        return value

    return value


def clean_dataframe_for_excel(df):
    """
    Make an entire DataFrame safe for Excel export.
    """

    if df is None:
        return pd.DataFrame()

    result = df.copy()

    # Absolute protection against duplicate column names.
    result.columns = make_unique_column_names(
        result.columns
    )

    for column in result.columns:
        result[column] = result[column].map(
            clean_excel_value
        )

    return result


# ============================================================
# STANDARD COLUMN NAMES
# ============================================================

STANDARD_COLUMNS = [
    "tree_id",
    "length_m",
    "diameter_cm",
    "age_years",
    "count_knots",
    "knot_diameter_mm",
    "count_cracks",
    "crack_length_cm",
    "crack_width_mm",
    "has_forking",
    "has_bend",
    "has_disease",
]


# ============================================================
# HEADER ALIASES
# ============================================================

HEADER_ALIASES = {

    "tree_id": [
        "tree id",
        "tree_id",
        "treeid",
        "tree number",
        "tree no",
        "tree nr",
        "tree",
        "log id",
        "log_id",
        "log number",
        "log no",
        "id",
    ],

    "length_m": [
        "length in m",
        "length_m",
        "length m",
        "length",
        "log length",
        "log_length",
        "log length m",
        "log_length_m",
        "stem length",
        "stem length m",
    ],

    "diameter_cm": [
        "diameter in cm",
        "diameter_cm",
        "diameter cm",
        "diameter",
        "log diameter",
        "log_diameter",
        "log diameter cm",
        "log_diameter_cm",
        "stem diameter",
        "stem diameter cm",
    ],

    "age_years": [
        "age in years",
        "age_years",
        "age years",
        "age",
        "tree age",
        "tree_age",
        "age of tree",
    ],

    "count_knots": [
        "count_knots",
        "count knots",
        "knot count",
        "knots count",
        "number of knots",
        "number knots",
        "knots",
    ],

    "knot_diameter_mm": [
        "knot_diameter_mm",
        "knot diameter mm",
        "knot diameter in mm",
        "knot diameters",
        "knot diameter",
        "knot size",
        "knot sizes",
    ],

    "count_cracks": [
        "count_cracks",
        "count cracks",
        "crack count",
        "cracks count",
        "number of cracks",
        "number cracks",
        "cracks",
    ],

    "crack_length_cm": [
        "crack_length_cm",
        "crack length cm",
        "crack length in cm",
        "crack lengths",
        "crack length",
        "crack size length",
    ],

    "crack_width_mm": [
        "crack_width_mm",
        "crack width mm",
        "crack width in mm",
        "crack widths",
        "crack width",
    ],

    "has_forking": [
        "has_forking",
        "has forking",
        "forking",
        "forked",
        "fork",
        "has fork",
    ],

    "has_bend": [
        "has_bend",
        "has bend",
        "bend",
        "bent",
        "has bending",
    ],

    "has_disease": [
        "has_disease",
        "has disease",
        "disease",
        "diseased",
        "health disease",
        "has health disease",
    ],
}


# ============================================================
# HEADER FUNCTIONS
# ============================================================

def normalize_header(value):

    if value is None:
        return ""

    text = str(value).strip().lower()

    text = text.replace("\n", " ")
    text = text.replace("\t", " ")

    text = re.sub(
        r"[_\-]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def header_match_key(value):

    text = normalize_header(value)

    # Handles pandas duplicate headers:
    # age in years
    # age in years.1
    # age in years.2

    text = re.sub(
        r"(?:[._\s]+)\d+$",
        "",
        text
    )

    return text.strip()


def build_alias_lookup():

    lookup = {}

    for canonical, aliases in HEADER_ALIASES.items():

        lookup[
            header_match_key(canonical)
        ] = canonical

        for alias in aliases:

            lookup[
                header_match_key(alias)
            ] = canonical

    return lookup


ALIAS_LOOKUP = build_alias_lookup()


# ============================================================
# UNIQUE COLUMN NAMES
# ============================================================

def make_unique_column_names(columns):

    result = []
    counts = {}

    for column in columns:

        base = str(column).strip()

        if base == "":
            base = "Unnamed"

        if base not in counts:

            counts[base] = 0
            result.append(base)

        else:

            counts[base] += 1

            result.append(
                f"{base}.{counts[base]}"
            )

    return result


# ============================================================
# SAFE NUMERIC FUNCTIONS
# ============================================================

def safe_number(value, default=0.0):

    if isinstance(value, pd.DataFrame):

        if value.empty:
            return default

        value = value.iloc[0, 0]

    elif isinstance(value, pd.Series):

        if value.empty:
            return default

        non_empty = value.dropna()

        if non_empty.empty:
            return default

        value = non_empty.iloc[0]

    if value is None:
        return default

    if isinstance(value, str):

        text = value.strip()

        if text == "":
            return default

        text = text.replace(
            ",",
            "."
        )

        try:
            result = float(text)

            if math.isfinite(result):
                return result

            return default

        except Exception:
            return default

    try:

        result = float(value)

        if math.isfinite(result):
            return result

        return default

    except Exception:
        return default


def safe_optional_number(value):

    if isinstance(value, pd.DataFrame):

        if value.empty:
            return np.nan

        value = value.iloc[0, 0]

    elif isinstance(value, pd.Series):

        if value.empty:
            return np.nan

        non_empty = value.dropna()

        if non_empty.empty:
            return np.nan

        value = non_empty.iloc[0]

    if value is None:
        return np.nan

    if isinstance(value, str):

        text = value.strip()

        if text == "":
            return np.nan

        text = text.replace(
            ",",
            "."
        )

        try:

            result = float(text)

            if math.isfinite(result):
                return result

            return np.nan

        except Exception:
            return np.nan

    try:

        result = float(value)

        if math.isfinite(result):
            return result

        return np.nan

    except Exception:
        return np.nan


def clamp(
    value,
    minimum=0.0,
    maximum=100.0
):

    value = safe_number(
        value,
        minimum
    )

    return max(
        minimum,
        min(
            maximum,
            value
        )
    )


# ============================================================
# BOOLEAN
# ============================================================

def to_bool(value):

    if isinstance(value, pd.DataFrame):

        if value.empty:
            return False

        value = value.iloc[0, 0]

    elif isinstance(value, pd.Series):

        if value.empty:
            return False

        non_empty = value.dropna()

        if non_empty.empty:
            return False

        value = non_empty.iloc[0]

    if value is None:
        return False

    if isinstance(value, bool):
        return value

    if isinstance(
        value,
        (
            int,
            float,
            np.integer,
            np.floating,
        ),
    ):

        if pd.isna(value):
            return False

        return float(value) != 0

    text = str(value).strip().lower()

    true_values = {
        "yes",
        "y",
        "true",
        "t",
        "1",
        "present",
        "positive",
        "forked",
        "bent",
        "diseased",
    }

    false_values = {
        "no",
        "n",
        "false",
        "f",
        "0",
        "none",
        "absent",
        "",
    }

    if text in true_values:
        return True

    if text in false_values:
        return False

    return False


# ============================================================
# VOLUME
# ============================================================

def calculate_volume(
    length_m,
    diameter_cm
):

    length_m = safe_number(
        length_m,
        0.0
    )

    diameter_cm = safe_number(
        diameter_cm,
        0.0
    )

    radius_m = (
        diameter_cm
        / 100.0
        / 2.0
    )

    return (
        math.pi
        * radius_m
        * radius_m
        * length_m
    )


# ============================================================
# PARSE MEASUREMENTS
# ============================================================

def parse_number_list(value):

    if isinstance(value, pd.DataFrame):

        if value.empty:
            return []

        value = value.iloc[0, 0]

    elif isinstance(value, pd.Series):

        if value.empty:
            return []

        non_empty = value.dropna()

        if non_empty.empty:
            return []

        value = non_empty.iloc[0]

    if value is None:
        return []

    if isinstance(
        value,
        (
            int,
            float,
            np.integer,
            np.floating,
        ),
    ):

        if pd.isna(value):
            return []

        return [float(value)]

    text = str(value).strip()

    if not text:
        return []

    text = re.sub(
        r"[,;\/|\\\s]+",
        " ",
        text
    )

    values = []

    for token in text.split():

        number = safe_optional_number(
            token
        )

        if not pd.isna(number):
            values.append(
                float(number)
            )

    return values


def average_list(values):

    if not values:
        return 0.0

    return float(
        np.mean(values)
    )


# ============================================================
# STANDARDIZE EXCEL COLUMNS
# ============================================================

def standardize_columns(df):

    warnings = []

    if df is None:
        raise ValueError(
            "No dataframe was supplied."
        )

    df = df.copy()

    # Critical fix:
    # Make the ORIGINAL Excel column names unique first.
    df.columns = make_unique_column_names(
        df.columns
    )

    canonical_series = {}
    extra_series = {}

    for original_column in df.columns:

        canonical = ALIAS_LOOKUP.get(
            header_match_key(
                original_column
            )
        )

        series = df[
            original_column
        ].copy()

        if isinstance(
            series,
            pd.DataFrame
        ):

            series = series.iloc[:, 0]

        if canonical is None:

            extra_name = str(
                original_column
            )

            while extra_name in extra_series:

                extra_name += "_extra"

            extra_series[
                extra_name
            ] = series

            continue

        if canonical not in canonical_series:

            canonical_series[
                canonical
            ] = series

        else:

            existing = (
                canonical_series[
                    canonical
                ]
                .reset_index(drop=True)
            )

            incoming = (
                series
                .reset_index(drop=True)
            )

            combined = (
                existing
                .combine_first(
                    incoming
                )
            )

            canonical_series[
                canonical
            ] = combined

            warnings.append(
                f"Multiple Excel columns were mapped "
                f"to '{canonical}'. Their non-empty "
                f"values were combined."
            )

    standardized = pd.DataFrame(
        index=df.index
    )

    for canonical in STANDARD_COLUMNS:

        if canonical in canonical_series:

            standardized[
                canonical
            ] = canonical_series[
                canonical
            ].values

        else:

            standardized[
                canonical
            ] = np.nan

    # Preserve unknown columns.
    for name, series in extra_series.items():

        safe_name = name

        if safe_name in standardized.columns:

            counter = 1

            while (
                f"{safe_name}_{counter}"
                in standardized.columns
            ):
                counter += 1

            safe_name = (
                f"{safe_name}_{counter}"
            )

        standardized[
            safe_name
        ] = series.values

    standardized.columns = (
        make_unique_column_names(
            standardized.columns
        )
    )

    return standardized, warnings


# ============================================================
# PREPARE DATAFRAME
# ============================================================

def prepare_dataframe(df):

    df = df.copy()

    for column in STANDARD_COLUMNS:

        if column not in df.columns:
            df[column] = np.nan

    # Numeric fields
    df["length_m"] = (
        df["length_m"]
        .apply(
            lambda x:
            safe_number(x, 0.0)
        )
    )

    df["diameter_cm"] = (
        df["diameter_cm"]
        .apply(
            lambda x:
            safe_number(x, 0.0)
        )
    )

    # Age is optional.
    df["age_years"] = (
        df["age_years"]
        .apply(
            safe_optional_number
        )
    )

    df["count_knots"] = (
        df["count_knots"]
        .apply(
            lambda x:
            max(
                0.0,
                safe_number(
                    x,
                    0.0
                )
            )
        )
    )

    df["count_cracks"] = (
        df["count_cracks"]
        .apply(
            lambda x:
            max(
                0.0,
                safe_number(
                    x,
                    0.0
                )
            )
        )
    )

    # Boolean fields
    df["has_forking"] = (
        df["has_forking"]
        .apply(to_bool)
    )

    df["has_bend"] = (
        df["has_bend"]
        .apply(to_bool)
    )

    df["has_disease"] = (
        df["has_disease"]
        .apply(to_bool)
    )

    # Knot measurements
    df[
        "Knot_Measurement_Count"
    ] = (
        df["knot_diameter_mm"]
        .apply(
            lambda x:
            len(
                parse_number_list(x)
            )
        )
    )

    df[
        "Average_Knot_Diameter_mm"
    ] = (
        df["knot_diameter_mm"]
        .apply(
            lambda x:
            average_list(
                parse_number_list(x)
            )
        )
    )

    # Crack length
    df[
        "Crack_Length_Measurement_Count"
    ] = (
        df["crack_length_cm"]
        .apply(
            lambda x:
            len(
                parse_number_list(x)
            )
        )
    )

    df[
        "Average_Crack_Length_cm"
    ] = (
        df["crack_length_cm"]
        .apply(
            lambda x:
            average_list(
                parse_number_list(x)
            )
        )
    )

    # Crack width
    df[
        "Crack_Width_Measurement_Count"
    ] = (
        df["crack_width_mm"]
        .apply(
            lambda x:
            len(
                parse_number_list(x)
            )
        )
    )

    df[
        "Average_Crack_Width_mm"
    ] = (
        df["crack_width_mm"]
        .apply(
            lambda x:
            average_list(
                parse_number_list(x)
            )
        )
    )

    # Checks
    df[
        "Knot_Count_Check"
    ] = df.apply(
        lambda row:
        (
            "OK"
            if (
                safe_number(
                    row["count_knots"]
                ) <= 0
                or safe_number(
                    row[
                        "Knot_Measurement_Count"
                    ]
                ) == 0
                or safe_number(
                    row[
                        "Knot_Measurement_Count"
                    ]
                )
                ==
                safe_number(
                    row["count_knots"]
                )
            )
            else "CHECK"
        ),
        axis=1
    )

    df[
        "Crack_Count_Check"
    ] = df.apply(
        lambda row:
        (
            "OK"
            if (
                safe_number(
                    row["count_cracks"]
                ) <= 0
                or safe_number(
                    row[
                        "Crack_Length_Measurement_Count"
                    ]
                ) == 0
            )
            else "CHECK"
        ),
        axis=1
    )

    return df


# ============================================================
# KNOT SCORING
# ============================================================

def knot_diameter_score(
    relative_percent
):

    if relative_percent <= 5:
        return 25.0

    if relative_percent <= 10:
        return 50.0

    if relative_percent <= 20:
        return 75.0

    return 100.0


def calculate_knot_penalty(row):

    count = max(
        0.0,
        safe_number(
            row["count_knots"],
            0.0
        )
    )

    average_diameter_mm = max(
        0.0,
        safe_number(
            row[
                "Average_Knot_Diameter_mm"
            ],
            0.0
        )
    )

    log_diameter_cm = max(
        0.0,
        safe_number(
            row["diameter_cm"],
            0.0
        )
    )

    if count <= 0:

        return {
            "Knot_Relative_Diameter_pct": 0.0,
            "Knot_Diameter_Score": 0.0,
            "Knot_Count_Penalty": 0.0,
            "Knot_Diameter_Penalty": 0.0,
            "Knot_Interaction_Penalty": 0.0,
            "Knot_Penalty": 0.0,
            "Knot_Assessment": "None",
        }

    if log_diameter_cm > 0:

        log_diameter_mm = (
            log_diameter_cm
            * 10.0
        )

        relative_percent = (
            average_diameter_mm
            / log_diameter_mm
            * 100.0
        )

    else:

        relative_percent = 100.0

    diameter_score = (
        knot_diameter_score(
            relative_percent
        )
    )

    count_penalty = min(
        count * 1.5,
        12.0
    )

    diameter_penalty = min(
        diameter_score * 0.12,
        12.0
    )

    interaction = 0.0

    if (
        count >= 5
        and diameter_score >= 75
    ):
        interaction = 5.0

    elif (
        count >= 3
        and diameter_score >= 75
    ):
        interaction = 3.0

    elif (
        count >= 5
        and diameter_score >= 50
    ):
        interaction = 2.0

    total = clamp(
        count_penalty
        + diameter_penalty
        + interaction,
        0.0,
        100.0
    )

    if total <= 25:
        assessment = "Low"

    elif total <= 50:
        assessment = "Moderate"

    elif total <= 75:
        assessment = "High"

    else:
        assessment = "Severe"

    return {
        "Knot_Relative_Diameter_pct":
            relative_percent,

        "Knot_Diameter_Score":
            diameter_score,

        "Knot_Count_Penalty":
            count_penalty,

        "Knot_Diameter_Penalty":
            diameter_penalty,

        "Knot_Interaction_Penalty":
            interaction,

        "Knot_Penalty":
            total,

        "Knot_Assessment":
            assessment,
    }


# ============================================================
# CRACK SCORING
# ============================================================

def crack_dimension_score(
    value,
    thresholds
):

    if value <= thresholds[0]:
        return 25.0

    if value <= thresholds[1]:
        return 50.0

    if value <= thresholds[2]:
        return 75.0

    return 100.0


def calculate_crack_penalty(row):

    count = max(
        0.0,
        safe_number(
            row["count_cracks"],
            0.0
        )
    )

    average_length_cm = max(
        0.0,
        safe_number(
            row[
                "Average_Crack_Length_cm"
            ],
            0.0
        )
    )

    average_width_mm = max(
        0.0,
        safe_number(
            row[
                "Average_Crack_Width_mm"
            ],
            0.0
        )
    )

    log_length_m = max(
        0.0,
        safe_number(
            row["length_m"],
            0.0
        )
    )

    if count <= 0:

        return {
            "Crack_Normalized_Length_pct": 0.0,
            "Crack_Length_Score": 0.0,
            "Crack_Width_Score": 0.0,
            "Crack_Count_Penalty": 0.0,
            "Crack_Dimension_Penalty": 0.0,
            "Crack_Interaction_Penalty": 0.0,
            "Crack_Penalty": 0.0,
            "Crack_Assessment": "None",
        }

    if log_length_m > 0:

        log_length_cm = (
            log_length_m
            * 100.0
        )

        normalized_length = (
            average_length_cm
            / log_length_cm
            * 100.0
        )

    else:

        normalized_length = 100.0

    length_score = (
        crack_dimension_score(
            normalized_length,
            (
                10,
                25,
                50
            )
        )
    )

    width_score = (
        crack_dimension_score(
            average_width_mm,
            (
                2,
                5,
                10
            )
        )
    )

    count_penalty = min(
        count * 1.5,
        12.0
    )

    combined_dimension_score = (
        length_score * 0.60
        + width_score * 0.40
    )

    dimension_penalty = min(
        combined_dimension_score
        * 0.20,
        20.0
    )

    interaction = 0.0

    if (
        count >= 5
        and combined_dimension_score >= 75
    ):
        interaction = 5.0

    elif (
        count >= 3
        and combined_dimension_score >= 75
    ):
        interaction = 3.0

    elif (
        count >= 5
        and combined_dimension_score >= 50
    ):
        interaction = 2.0

    total = clamp(
        count_penalty
        + dimension_penalty
        + interaction,
        0.0,
        100.0
    )

    if (
        average_width_mm >= 10
        or normalized_length >= 50
    ):
        assessment = "Critical"

    elif total <= 25:
        assessment = "Low"

    elif total <= 50:
        assessment = "Moderate"

    elif total <= 75:
        assessment = "High"

    else:
        assessment = "Severe"

    return {
        "Crack_Normalized_Length_pct":
            normalized_length,

        "Crack_Length_Score":
            length_score,

        "Crack_Width_Score":
            width_score,

        "Crack_Count_Penalty":
            count_penalty,

        "Crack_Dimension_Penalty":
            dimension_penalty,

        "Crack_Interaction_Penalty":
            interaction,

        "Crack_Penalty":
            total,

        "Crack_Assessment":
            assessment,
    }


# ============================================================
# SIZE SCORING
# ============================================================

def calculate_size_score(
    length_m,
    diameter_cm
):

    length_m = safe_number(
        length_m,
        0.0
    )

    diameter_cm = safe_number(
        diameter_cm,
        0.0
    )

    length_clamped = clamp(
        length_m,
        MIN_LOG_LENGTH_M,
        MAX_LOG_LENGTH_M
    )

    diameter_clamped = clamp(
        diameter_cm,
        MIN_LOG_DIAMETER_CM,
        MAX_LOG_DIAMETER_CM
    )

    length_component = (
        (
            length_clamped
            - MIN_LOG_LENGTH_M
        )
        /
        (
            MAX_LOG_LENGTH_M
            - MIN_LOG_LENGTH_M
        )
        * 45.0
    )

    diameter_component = (
        (
            diameter_clamped
            - MIN_LOG_DIAMETER_CM
        )
        /
        (
            MAX_LOG_DIAMETER_CM
            - MIN_LOG_DIAMETER_CM
        )
        * 45.0
    )

    total = clamp(
        length_component
        + diameter_component,
        0.0,
        90.0
    )

    return {
        "Length_Score_Component":
            length_component,

        "Diameter_Score_Component":
            diameter_component,

        "Size_Score":
            total,
    }


# ============================================================
# QUALITY CLASS
# ============================================================

def quality_class(score):

    score = safe_number(
        score,
        0.0
    )

    if score >= 80:
        return "High"

    if score >= 60:
        return "Medium"

    if score >= 40:
        return "Low"

    return "Very Low"


# ============================================================
# ROW EVALUATION
# ============================================================

def evaluate_row(row):

    length_m = safe_number(
        row["length_m"],
        0.0
    )

    diameter_cm = safe_number(
        row["diameter_cm"],
        0.0
    )

    knot_result = (
        calculate_knot_penalty(row)
    )

    crack_result = (
        calculate_crack_penalty(row)
    )

    size_result = (
        calculate_size_score(
            length_m,
            diameter_cm
        )
    )

    forking_penalty = (
        8.0
        if to_bool(
            row["has_forking"]
        )
        else 0.0
    )

    bend_penalty = (
        8.0
        if to_bool(
            row["has_bend"]
        )
        else 0.0
    )

    disease_penalty = (
        15.0
        if to_bool(
            row["has_disease"]
        )
        else 0.0
    )

    other_defect_penalty = (
        forking_penalty
        + bend_penalty
        + disease_penalty
    )

    count_knots = safe_number(
        row["count_knots"],
        0.0
    )

    count_cracks = safe_number(
        row["count_cracks"],
        0.0
    )

    no_defects = (
        count_knots <= 0
        and count_cracks <= 0
        and not to_bool(
            row["has_forking"]
        )
        and not to_bool(
            row["has_bend"]
        )
        and not to_bool(
            row["has_disease"]
        )
    )

    no_defects_bonus = (
        10.0
        if no_defects
        else 0.0
    )

    final_score = (
        size_result["Size_Score"]
        - knot_result["Knot_Penalty"]
        - crack_result["Crack_Penalty"]
        - other_defect_penalty
        + no_defects_bonus
    )

    final_score = clamp(
        final_score,
        0.0,
        100.0
    )

    result = {}

    result.update(
        size_result
    )

    result.update(
        knot_result
    )

    result.update(
        crack_result
    )

    result[
        "Forking_Penalty"
    ] = forking_penalty

    result[
        "Bend_Penalty"
    ] = bend_penalty

    result[
        "Disease_Penalty"
    ] = disease_penalty

    result[
        "Other_Defect_Penalty"
    ] = other_defect_penalty

    result[
        "No_Defects_Bonus"
    ] = no_defects_bonus

    result[
        "Final_Quality_Score"
    ] = final_score

    result[
        "Quality_Class"
    ] = quality_class(
        final_score
    )

    # --------------------------------------------------------
    # Age
    #
    # Age is retained but NOT used in scoring.
    # --------------------------------------------------------

    age = safe_optional_number(
        row["age_years"]
    )

    result[
        "Age_Used_In_Scoring"
    ] = "No"

    if pd.isna(age):

        result[
            "Age_Status"
        ] = "Missing / Not Used"

    elif (
        age < MIN_PLAUSIBLE_AGE_YEARS
        or age > MAX_PLAUSIBLE_AGE_YEARS
    ):

        result[
            "Age_Status"
        ] = "Check"

    else:

        result[
            "Age_Status"
        ] = "Plausible / Not Used"

    return pd.Series(
        result
    )


# ============================================================
# FIND TARGET COLUMN
# ============================================================

def find_calibration_target(df):

    target_aliases = [
        "quality",
        "quality class",
        "quality_class",
        "expert quality",
        "expert grade",
        "expert rating",
        "target quality",
        "target",
        "ground truth",
        "reference quality",
        "manual quality",
    ]

    target_lookup = {
        header_match_key(x)
        for x in target_aliases
    }

    for column in df.columns:

        if (
            header_match_key(column)
            in target_lookup
        ):
            return column

    return None


# ============================================================
# DATA PLAUSIBILITY AUDIT
# ============================================================

def audit_data_plausibility(df):

    audit_rows = []

    row_count = len(df)

    strong_issues = []
    warnings = []

    if row_count == 0:

        return {
            "status": "NO_DATA",
            "summary":
                "No rows were loaded.",
            "row_count": 0,
            "warning_count": 0,
            "strong_issue_count": 0,
            "warnings": [],
            "strong_issues": [],
            "audit_rows": [],
        }

    for index, row in df.iterrows():

        excel_row = index + 2

        length_m = safe_number(
            row["length_m"],
            0.0
        )

        diameter_cm = safe_number(
            row["diameter_cm"],
            0.0
        )

        age_years = (
            safe_optional_number(
                row["age_years"]
            )
        )

        knot_count = safe_number(
            row["count_knots"],
            0.0
        )

        crack_count = safe_number(
            row["count_cracks"],
            0.0
        )

        knot_diameter = safe_number(
            row[
                "Average_Knot_Diameter_mm"
            ],
            0.0
        )

        crack_length = safe_number(
            row[
                "Average_Crack_Length_cm"
            ],
            0.0
        )

        crack_width = safe_number(
            row[
                "Average_Crack_Width_mm"
            ],
            0.0
        )

        row_warnings = []
        row_strong = []

        # Length
        if length_m <= 0:

            row_strong.append(
                "Missing or non-positive log length"
            )

        elif (
            length_m
            < MIN_PLAUSIBLE_LOG_LENGTH_M
            or
            length_m
            > MAX_PLAUSIBLE_LOG_LENGTH_M
        ):

            row_warnings.append(
                f"Length {length_m:g} m is outside "
                f"the usual plausibility range "
                f"({MIN_PLAUSIBLE_LOG_LENGTH_M:g}-"
                f"{MAX_PLAUSIBLE_LOG_LENGTH_M:g} m)"
            )

        if length_m >= STRONG_TEST_LENGTH_M:

            row_strong.append(
                f"Extreme log length: "
                f"{length_m:g} m"
            )

        # Diameter
        if diameter_cm <= 0:

            row_strong.append(
                "Missing or non-positive diameter"
            )

        elif (
            diameter_cm
            < MIN_PLAUSIBLE_DIAMETER_CM
            or
            diameter_cm
            > MAX_PLAUSIBLE_DIAMETER_CM
        ):

            row_warnings.append(
                f"Diameter {diameter_cm:g} cm "
                f"is outside the usual "
                f"plausibility range"
            )

        if diameter_cm >= STRONG_TEST_DIAMETER_CM:

            row_strong.append(
                f"Extreme diameter: "
                f"{diameter_cm:g} cm"
            )

        # Age
        if not pd.isna(age_years):

            if (
                age_years
                < MIN_PLAUSIBLE_AGE_YEARS
                or
                age_years
                > MAX_PLAUSIBLE_AGE_YEARS
            ):

                row_warnings.append(
                    f"Age {age_years:g} years "
                    f"is outside the plausibility range"
                )

            if age_years >= STRONG_TEST_AGE_YEARS:

                row_strong.append(
                    f"Extreme age value: "
                    f"{age_years:g} years"
                )

        # Knots
        if knot_count < 0:

            row_strong.append(
                "Negative knot count"
            )

        elif knot_count > MAX_PLAUSIBLE_KNOT_COUNT:

            row_warnings.append(
                f"Very high knot count: "
                f"{knot_count:g}"
            )

        # Cracks
        if crack_count < 0:

            row_strong.append(
                "Negative crack count"
            )

        elif crack_count > MAX_PLAUSIBLE_CRACK_COUNT:

            row_warnings.append(
                f"Very high crack count: "
                f"{crack_count:g}"
            )

        # Knot diameter
        if (
            knot_diameter
            > MAX_PLAUSIBLE_KNOT_DIAMETER_MM
        ):

            row_warnings.append(
                f"Very large knot diameter: "
                f"{knot_diameter:g} mm"
            )

        # Crack length
        if (
            crack_length
            > MAX_PLAUSIBLE_CRACK_LENGTH_CM
        ):

            row_warnings.append(
                f"Very large crack length: "
                f"{crack_length:g} cm"
            )

        # Crack width
        if (
            crack_width
            > MAX_PLAUSIBLE_CRACK_WIDTH_MM
        ):

            row_warnings.append(
                f"Very large crack width: "
                f"{crack_width:g} mm"
            )

        # Knot measurement consistency
        knot_measurement_count = (
            safe_number(
                row[
                    "Knot_Measurement_Count"
                ],
                0
            )
        )

        if (
            knot_count > 0
            and knot_measurement_count > 0
            and knot_measurement_count
            != knot_count
        ):

            row_warnings.append(
                "Knot count does not match "
                "number of knot measurements"
            )

        # Crack measurement consistency
        crack_length_measurement_count = (
            safe_number(
                row[
                    "Crack_Length_Measurement_Count"
                ],
                0
            )
        )

        if (
            crack_count > 0
            and crack_length_measurement_count > 0
            and crack_length_measurement_count
            != crack_count
        ):

            row_warnings.append(
                "Crack count does not match "
                "number of crack-length measurements"
            )

        if row_strong:

            strong_issues.extend(
                [
                    f"Row {excel_row}: {message}"
                    for message in row_strong
                ]
            )

        if row_warnings:

            warnings.extend(
                [
                    f"Row {excel_row}: {message}"
                    for message in row_warnings
                ]
            )

        audit_rows.append({
            "Excel_Row": excel_row,
            "Length_m": length_m,
            "Diameter_cm": diameter_cm,
            "Age_years":
                ""
                if pd.isna(age_years)
                else age_years,
            "Row_Warnings":
                " | ".join(
                    row_warnings
                ),
            "Strong_Issues":
                " | ".join(
                    row_strong
                ),
        })

    # Duplicate row check
    try:

        duplicate_count = int(
            df.duplicated(
                subset=[
                    "length_m",
                    "diameter_cm",
                    "age_years",
                    "count_knots",
                    "Average_Knot_Diameter_mm",
                    "count_cracks",
                    "Average_Crack_Length_cm",
                    "Average_Crack_Width_mm",
                    "has_forking",
                    "has_bend",
                    "has_disease",
                ],
                keep=False,
            ).sum()
        )

        duplicate_ratio = (
            duplicate_count
            / row_count
        )

        if (
            duplicate_ratio
            >= DUPLICATE_ROW_WARNING_RATIO
        ):

            warnings.append(
                f"High duplicate-row ratio: "
                f"{duplicate_ratio * 100:.1f}%"
            )

    except Exception as exc:

        warnings.append(
            "Duplicate-row check could not "
            f"be completed: {exc}"
        )

    # Status
    if strong_issues:

        status = (
            "TEST_OR_IMPLAUSIBLE"
        )

        summary = (
            "The dataset contains strong "
            "plausibility problems or values "
            "that look test/synthetic/"
            "implausible. Evaluation can "
            "still continue."
        )

    elif warnings:

        status = (
            "REALISTIC_WITH_WARNINGS"
        )

        summary = (
            "The dataset is broadly plausible, "
            "but some values require review."
        )

    else:

        status = (
            "REALISTIC_UNVERIFIED"
        )

        summary = (
            "No major plausibility problems "
            "were detected. This does not "
            "prove that the data are real."
        )

    if row_count < 5:

        warnings.append(
            "Fewer than 5 rows are available. "
            "This is too little data for "
            "meaningful statistical calibration."
        )

    return {
        "status": status,
        "summary": summary,
        "row_count": row_count,
        "warning_count": len(warnings),
        "strong_issue_count":
            len(strong_issues),
        "warnings": warnings,
        "strong_issues": strong_issues,
        "audit_rows": audit_rows,
    }


# ============================================================
# CALIBRATION REPORT
# ============================================================

def calibration_report(
    df,
    standardization_warnings=None
):

    if standardization_warnings is None:
        standardization_warnings = []

    audit = audit_data_plausibility(
        df
    )

    target_column = (
        find_calibration_target(df)
    )

    if target_column:

        target_status = (
            f"Reference/target column detected: "
            f"{target_column}. "
            f"No supervised calibration was "
            f"performed automatically."
        )

    else:

        target_status = (
            "No expert/reference target column "
            "was detected. Current calibration "
            "is a plausibility/readiness "
            "assessment, not supervised "
            "statistical calibration."
        )

    return {
        "Status":
            audit["status"],

        "Summary":
            audit["summary"],

        "Rows":
            audit["row_count"],

        "Warnings":
            audit["warning_count"],

        "Strong_Issues":
            audit["strong_issue_count"],

        "Target_Column":
            target_column
            if target_column
            else "",

        "Target_Status":
            target_status,

        "Standardization_Warnings":
            " | ".join(
                standardization_warnings
            ),

        "Warning_Details":
            " | ".join(
                audit["warnings"]
            ),

        "Strong_Issue_Details":
            " | ".join(
                audit["strong_issues"]
            ),

        "audit_rows":
            audit["audit_rows"],
    }


# ============================================================
# DATA DICTIONARY
# ============================================================

def create_data_dictionary():

    rows = [

        [
            "tree_id",
            "Tree/log identifier",
            "No",
        ],

        [
            "length_m",
            "Log/stem length in metres",
            "Yes",
        ],

        [
            "diameter_cm",
            "Log/stem diameter in centimetres",
            "Yes",
        ],

        [
            "age_years",
            "Tree age in years; optional; "
            "retained for future calibration; "
            "NOT used in current score",
            "No",
        ],

        [
            "count_knots",
            "Number of knots",
            "Yes",
        ],

        [
            "knot_diameter_mm",
            "Knot diameter measurement(s) in mm",
            "Yes",
        ],

        [
            "count_cracks",
            "Number of cracks",
            "Yes",
        ],

        [
            "crack_length_cm",
            "Crack length measurement(s) in cm",
            "Yes",
        ],

        [
            "crack_width_mm",
            "Crack width measurement(s) in mm",
            "Yes",
        ],

        [
            "has_forking",
            "Whether forking is present",
            "Yes",
        ],

        [
            "has_bend",
            "Whether bending is present",
            "Yes",
        ],

        [
            "has_disease",
            "Whether disease is present",
            "Yes",
        ],

        [
            "Final_Quality_Score",
            "Final calculated quality score, 0-100",
            "Calculated",
        ],

        [
            "Quality_Class",
            "High / Medium / Low / Very Low",
            "Calculated",
        ],

        [
            "Age_Used_In_Scoring",
            "Always No in current model",
            "Calculated",
        ],

        [
            "Age_Status",
            "Age plausibility status",
            "Calculated",
        ],
    ]

    return pd.DataFrame(
        rows,
        columns=[
            "Column",
            "Description",
            "Required / Calculated",
        ],
    )


# ============================================================
# MAIN GUI
# ============================================================

class ForestQualityApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            APP_TITLE
        )

        self.root.geometry(
            "1550x900"
        )

        self.root.minsize(
            1100,
            700
        )

        self.raw_df = None
        self.df = None

        self.standardization_warnings = []

        self.calibration_result = None

        self.last_file = None

        self.status_var = (
            tk.StringVar(
                value="No Excel file loaded."
            )
        )

        self.create_widgets()

    # ========================================================
    # GUI
    # ========================================================

    def create_widgets(self):

        top_frame = ttk.Frame(
            self.root
        )

        top_frame.pack(
            fill="x",
            padx=10,
            pady=10
        )

        ttk.Button(
            top_frame,
            text="Load Excel",
            command=self.load_excel,
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            top_frame,
            text="Calibrated",
            command=self.run_calibration,
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            top_frame,
            text="Run Evaluation",
            command=self.run_evaluation,
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            top_frame,
            text="Save Evaluated Excel",
            command=self.save_excel,
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            top_frame,
            text="Create Empty Template",
            command=self.create_template,
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            top_frame,
            text="Show Bar Chart",
            command=self.show_bar_chart,
        ).pack(
            side="left",
            padx=4
        )

        ttk.Button(
            top_frame,
            text="Show Pie Chart",
            command=self.show_pie_chart,
        ).pack(
            side="left",
            padx=4
        )

        status_frame = ttk.Frame(
            self.root
        )

        status_frame.pack(
            fill="x",
            padx=10,
            pady=(0, 8)
        )

        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            anchor="w",
        ).pack(
            fill="x"
        )

        table_frame = ttk.Frame(
            self.root
        )

        table_frame.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=5
        )

        self.tree = ttk.Treeview(
            table_frame,
            show="headings"
        )

        vertical_scroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview,
        )

        horizontal_scroll = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview,
        )

        self.tree.configure(
            yscrollcommand=
            vertical_scroll.set,

            xscrollcommand=
            horizontal_scroll.set,
        )

        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        vertical_scroll.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        horizontal_scroll.grid(
            row=1,
            column=0,
            sticky="ew"
        )

        table_frame.rowconfigure(
            0,
            weight=1
        )

        table_frame.columnconfigure(
            0,
            weight=1
        )

    # ========================================================
    # LOAD EXCEL
    # ========================================================

    def load_excel(self):

        filename = filedialog.askopenfilename(
            title="Select Excel file",

            filetypes=[
                (
                    "Excel files",
                    "*.xlsx *.xls"
                ),
                (
                    "All files",
                    "*.*"
                ),
            ],
        )

        if not filename:
            return

        try:

            raw_df = pd.read_excel(
                filename,
                sheet_name=0
            )

            if raw_df is None:
                raise ValueError(
                    "The Excel file contains no data."
                )

            if raw_df.empty:
                raise ValueError(
                    "The first Excel sheet is empty."
                )

            self.raw_df = (
                raw_df.copy()
            )

            standardized, warnings = (
                standardize_columns(
                    raw_df
                )
            )

            self.standardization_warnings = (
                warnings
            )

            self.df = (
                prepare_dataframe(
                    standardized
                )
            )

            self.last_file = filename

            self.calibration_result = None

            self.display_dataframe(
                self.df
            )

            self.status_var.set(
                f"Loaded: {filename} | "
                f"{len(self.df)} rows | "
                f"{len(self.df.columns)} columns"
            )

            warning_text = ""

            if warnings:

                warning_text = (
                    "\n\nColumn warnings:\n- "
                    + "\n- ".join(
                        warnings
                    )
                )

            messagebox.showinfo(
                "Excel Loaded",
                "Excel file loaded successfully."
                + warning_text
            )

        except Exception as exc:

            messagebox.showerror(
                "Load Error",
                "Could not load the Excel file:\n\n"
                f"{type(exc).__name__}: {exc}"
            )

    # ========================================================
    # CALIBRATION
    # ========================================================

    def run_calibration(self):

        if self.df is None:

            messagebox.showwarning(
                "No Data",
                "Please load an Excel file first."
            )

            return

        try:

            self.calibration_result = (
                calibration_report(
                    self.df,
                    self.standardization_warnings
                )
            )

            result = (
                self.calibration_result
            )

            status = result[
                "Status"
            ]

            if (
                status
                == "TEST_OR_IMPLAUSIBLE"
            ):

                messagebox.showwarning(
                    "Calibration Warning",

                    "The loaded data contain "
                    "strong plausibility problems "
                    "or values that look "
                    "test/synthetic/implausible."
                    "\n\n"
                    f"{result['Summary']}"
                    "\n\n"
                    f"Rows: {result['Rows']}"
                    "\n"
                    f"Warnings: {result['Warnings']}"
                    "\n"
                    f"Strong issues: "
                    f"{result['Strong_Issues']}"
                    "\n\n"
                    "This does NOT prove that the "
                    "data are fake."
                    "\n\n"
                    "Evaluation will continue normally."
                )

            elif (
                status
                == "REALISTIC_WITH_WARNINGS"
            ):

                messagebox.showwarning(
                    "Calibration Result",

                    f"{result['Summary']}"
                    "\n\n"
                    f"Rows: {result['Rows']}"
                    "\n"
                    f"Warnings: {result['Warnings']}"
                    "\n"
                    f"Strong issues: "
                    f"{result['Strong_Issues']}"
                    "\n\n"
                    "Evaluation can continue."
                )

            elif (
                status
                == "REALISTIC_UNVERIFIED"
            ):

                messagebox.showinfo(
                    "Calibration Result",

                    f"{result['Summary']}"
                    "\n\n"
                    f"Rows: {result['Rows']}"
                    "\n\n"
                    "This is a plausibility check, "
                    "not proof that the data are real."
                )

            else:

                messagebox.showwarning(
                    "Calibration",
                    result["Summary"]
                )

            self.status_var.set(
                f"Calibration: {status}"
            )

        except Exception as exc:

            messagebox.showerror(
                "Calibration Error",

                "Calibration could not be completed:"
                "\n\n"
                f"{type(exc).__name__}: {exc}"
            )

    # ========================================================
    # RUN EVALUATION
    # ========================================================

    def run_evaluation(
        self,
        show_message=True
    ):

        if self.df is None:

            messagebox.showwarning(
                "No Data",
                "Please load an Excel file first."
            )

            return False

        try:

            self.df = (
                prepare_dataframe(
                    self.df
                )
            )

            evaluation = (
                self.df.apply(
                    evaluate_row,
                    axis=1
                )
            )

            # Make sure there are no duplicate output columns.
            output_columns = [
                column
                for column
                in evaluation.columns
                if column
                not in self.df.columns
            ]

            self.df = pd.concat(
                [
                    self.df.reset_index(
                        drop=True
                    ),

                    evaluation[
                        output_columns
                    ].reset_index(
                        drop=True
                    ),
                ],
                axis=1
            )

            self.df.columns = (
                make_unique_column_names(
                    self.df.columns
                )
            )

            self.display_dataframe(
                self.df
            )

            self.status_var.set(
                f"Evaluation completed: "
                f"{len(self.df)} rows."
            )

            if show_message:

                messagebox.showinfo(
                    "Evaluation Complete",

                    "Evaluation completed successfully."
                    "\n\n"
                    "Age was retained for future "
                    "use but was NOT used in "
                    "the current quality score."
                )

            return True

        except Exception as exc:

            messagebox.showerror(
                "Evaluation Error",

                "Evaluation failed:"
                "\n\n"
                f"{type(exc).__name__}: {exc}"
            )

            return False

    # ========================================================
    # DISPLAY DATA
    # ========================================================

    def display_dataframe(self, df):

        self.tree.delete(
            *self.tree.get_children()
        )

        if df is None:
            return

        display_df = df.copy()

        display_df.columns = (
            make_unique_column_names(
                display_df.columns
            )
        )

        columns = list(
            display_df.columns
        )

        self.tree["columns"] = (
            columns
        )

        for column in columns:

            self.tree.heading(
                column,
                text=str(column)
            )

            self.tree.column(
                column,
                width=130,
                minwidth=80,
                anchor="center"
            )

        for index, row in (
            display_df.iterrows()
        ):

            values = []

            for column in columns:

                value = row[
                    column
                ]

                if pd.isna(value):

                    value = ""

                elif isinstance(
                    value,
                    float
                ):

                    if value.is_integer():

                        value = int(value)

                    else:

                        value = round(
                            value,
                            3
                        )

                values.append(
                    value
                )

            item_id = (
                self.tree.insert(
                    "",
                    "end",
                    values=values
                )
            )

            if (
                "Quality_Class"
                in columns
            ):

                quality_index = (
                    columns.index(
                        "Quality_Class"
                    )
                )

                quality = values[
                    quality_index
                ]

                if quality == "High":
                    tag = "quality_high"

                elif quality == "Medium":
                    tag = "quality_medium"

                elif quality == "Low":
                    tag = "quality_low"

                elif quality == "Very Low":
                    tag = "quality_very_low"

                else:
                    tag = ""

                if tag:

                    self.tree.item(
                        item_id,
                        tags=(tag,)
                    )

        self.tree.tag_configure(
            "quality_high",
            background="#C6EFCE"
        )

        self.tree.tag_configure(
            "quality_medium",
            background="#FFEB9C"
        )

        self.tree.tag_configure(
            "quality_low",
            background="#F4B183"
        )

        self.tree.tag_configure(
            "quality_very_low",
            background="#F4CCCC"
        )

    # ========================================================
    # SAVE EXCEL
    # ========================================================

    def save_excel(self):

        if self.df is None:

            messagebox.showwarning(
                "No Data",
                "There is no data to save."
            )

            return

        filename = filedialog.asksaveasfilename(
            title="Save evaluated Excel file",

            defaultextension=".xlsx",

            filetypes=[
                (
                    "Excel files",
                    "*.xlsx"
                )
            ],
        )

        if not filename:
            return

        try:

            # ------------------------------------------------
            # STEP 1: Make sure evaluation exists
            # ------------------------------------------------

            if (
                "Final_Quality_Score"
                not in self.df.columns
            ):

                success = (
                    self.run_evaluation(
                        show_message=False
                    )
                )

                if not success:
                    return

            # ------------------------------------------------
            # STEP 2: Calibration audit
            # ------------------------------------------------

            if (
                self.calibration_result
                is None
            ):

                self.calibration_result = (
                    calibration_report(
                        self.df,
                        self.standardization_warnings
                    )
                )

            calibration = (
                self.calibration_result
            )

            # ------------------------------------------------
            # STEP 3: Evaluated Data
            # ------------------------------------------------

            evaluated_df = (
                clean_dataframe_for_excel(
                    self.df
                )
            )

            # ------------------------------------------------
            # STEP 4: Calibration Audit
            # ------------------------------------------------

            calibration_rows = [
                [
                    "Status",
                    calibration["Status"],
                ],

                [
                    "Summary",
                    calibration["Summary"],
                ],

                [
                    "Rows",
                    calibration["Rows"],
                ],

                [
                    "Warnings",
                    calibration["Warnings"],
                ],

                [
                    "Strong Issues",
                    calibration[
                        "Strong_Issues"
                    ],
                ],

                [
                    "Target Column",
                    calibration[
                        "Target_Column"
                    ],
                ],

                [
                    "Target Status",
                    calibration[
                        "Target_Status"
                    ],
                ],

                [
                    "Standardization Warnings",
                    calibration[
                        "Standardization_Warnings"
                    ],
                ],

                [
                    "Warning Details",
                    calibration[
                        "Warning_Details"
                    ],
                ],

                [
                    "Strong Issue Details",
                    calibration[
                        "Strong_Issue_Details"
                    ],
                ],
            ]

            calibration_df = pd.DataFrame(
                calibration_rows,
                columns=[
                    "Item",
                    "Value",
                ],
            )

            calibration_df = (
                clean_dataframe_for_excel(
                    calibration_df
                )
            )

            # ------------------------------------------------
            # STEP 5: Row Audit
            # ------------------------------------------------

            audit_rows = (
                calibration.get(
                    "audit_rows",
                    []
                )
            )

            if (
                isinstance(
                    audit_rows,
                    list
                )
                and audit_rows
            ):

                row_audit_df = (
                    pd.DataFrame(
                        audit_rows
                    )
                )

            else:

                # Always create a valid sheet.
                row_audit_df = pd.DataFrame(
                    {
                        "Message": [
                            "No row-level audit records."
                        ]
                    }
                )

            row_audit_df = (
                clean_dataframe_for_excel(
                    row_audit_df
                )
            )

            # ------------------------------------------------
            # STEP 6: Data Dictionary
            # ------------------------------------------------

            dictionary_df = (
                create_data_dictionary()
            )

            dictionary_df = (
                clean_dataframe_for_excel(
                    dictionary_df
                )
            )

            # ------------------------------------------------
            # STEP 7: Write workbook
            # ------------------------------------------------

            with pd.ExcelWriter(
                filename,
                engine="openpyxl",
                mode="w"
            ) as writer:

                evaluated_df.to_excel(
                    writer,
                    sheet_name="Evaluated Data",
                    index=False
                )

                calibration_df.to_excel(
                    writer,
                    sheet_name="Calibration_Audit",
                    index=False
                )

                row_audit_df.to_excel(
                    writer,
                    sheet_name="Row_Audit",
                    index=False
                )

                dictionary_df.to_excel(
                    writer,
                    sheet_name="Data_Dictionary",
                    index=False
                )

            # ------------------------------------------------
            # STEP 8: Format workbook
            # ------------------------------------------------

            self.format_saved_workbook(
                filename
            )

            self.status_var.set(
                f"Saved successfully: {filename}"
            )

            messagebox.showinfo(
                "Excel Saved",

                "The evaluated Excel file was "
                "saved successfully.\n\n"
                f"{filename}"
            )

        except PermissionError:

            messagebox.showerror(
                "Save Error",

                "Excel could not save the file "
                "because the destination file "
                "is probably already open in "
                "Microsoft Excel.\n\n"
                "Close the Excel file and try again."
            )

        except OSError as exc:

            messagebox.showerror(
                "Save Error",

                "The operating system could not "
                "create the Excel file.\n\n"
                f"{type(exc).__name__}: {exc}"
            )

        except Exception as exc:

            messagebox.showerror(
                "Save Error",

                "The evaluation was completed, "
                "but Excel export failed.\n\n"

                f"Error type:\n"
                f"{type(exc).__name__}\n\n"

                f"Error message:\n"
                f"{exc}\n\n"

                "The problem is in the Excel "
                "export stage, not necessarily "
                "in the scoring calculation."
            )

    # ========================================================
    # FORMAT SAVED WORKBOOK
    # ========================================================

    def format_saved_workbook(
        self,
        filename
    ):

        workbook = openpyxl.load_workbook(
            filename
        )

        header_fill = PatternFill(
            fill_type="solid",
            fgColor="1F4E78"
        )

        header_font = Font(
            bold=True,
            color="FFFFFF"
        )

        quality_high_fill = PatternFill(
            fill_type="solid",
            fgColor="C6EFCE"
        )

        quality_medium_fill = PatternFill(
            fill_type="solid",
            fgColor="FFEB9C"
        )

        quality_low_fill = PatternFill(
            fill_type="solid",
            fgColor="F4B183"
        )

        quality_very_low_fill = PatternFill(
            fill_type="solid",
            fgColor="F4CCCC"
        )

        warning_fill = PatternFill(
            fill_type="solid",
            fgColor="FFF2CC"
        )

        strong_fill = PatternFill(
            fill_type="solid",
            fgColor="F4CCCC"
        )

        for sheet in workbook.worksheets:

            sheet.freeze_panes = "A2"

            # Autofilter only if the sheet has
            # at least one row/column.
            if (
                sheet.max_row >= 1
                and sheet.max_column >= 1
            ):

                sheet.auto_filter.ref = (
                    sheet.dimensions
                )

            for cell in sheet[1]:

                cell.fill = header_fill

                cell.font = header_font

                cell.alignment = (
                    Alignment(
                        horizontal="center",
                        vertical="center",
                        wrap_text=True
                    )
                )

            # ------------------------------------------------
            # Column widths
            # ------------------------------------------------

            for column_cells in (
                sheet.columns
            ):

                max_length = 0

                column_letter = (
                    get_column_letter(
                        column_cells[0].column
                    )
                )

                for cell in column_cells:

                    try:

                        value_length = len(
                            str(
                                cell.value
                            )
                        )

                        # Don't make columns enormous
                        # because of audit messages.
                        max_length = max(
                            max_length,
                            min(
                                value_length,
                                40
                            )
                        )

                    except Exception:
                        pass

                sheet.column_dimensions[
                    column_letter
                ].width = min(
                    max(
                        max_length + 2,
                        12
                    ),
                    45
                )

        # ----------------------------------------------------
        # Evaluated Data quality colors
        # ----------------------------------------------------

        if (
            "Evaluated Data"
            in workbook.sheetnames
        ):

            sheet = workbook[
                "Evaluated Data"
            ]

            headers = [
                cell.value
                for cell in sheet[1]
            ]

            if (
                "Quality_Class"
                in headers
            ):

                quality_col = (
                    headers.index(
                        "Quality_Class"
                    )
                    + 1
                )

                for row in range(
                    2,
                    sheet.max_row + 1
                ):

                    cell = sheet.cell(
                        row=row,
                        column=quality_col
                    )

                    value = cell.value

                    if value == "High":

                        cell.fill = (
                            quality_high_fill
                        )

                    elif value == "Medium":

                        cell.fill = (
                            quality_medium_fill
                        )

                    elif value == "Low":

                        cell.fill = (
                            quality_low_fill
                        )

                    elif value == "Very Low":

                        cell.fill = (
                            quality_very_low_fill
                        )

        # ----------------------------------------------------
        # Calibration audit formatting
        # ----------------------------------------------------

        if (
            "Calibration_Audit"
            in workbook.sheetnames
        ):

            sheet = workbook[
                "Calibration_Audit"
            ]

            for row in range(
                2,
                sheet.max_row + 1
            ):

                item = sheet.cell(
                    row=row,
                    column=1
                ).value

                value_cell = sheet.cell(
                    row=row,
                    column=2
                )

                value = str(
                    value_cell.value
                )

                if item == "Status":

                    if (
                        value
                        == "TEST_OR_IMPLAUSIBLE"
                    ):

                        value_cell.fill = (
                            strong_fill
                        )

                    elif (
                        value
                        == "REALISTIC_WITH_WARNINGS"
                    ):

                        value_cell.fill = (
                            warning_fill
                        )

        # ----------------------------------------------------
        # Row audit formatting
        # ----------------------------------------------------

        if (
            "Row_Audit"
            in workbook.sheetnames
        ):

            sheet = workbook[
                "Row_Audit"
            ]

            headers = [
                cell.value
                for cell in sheet[1]
            ]

            if (
                "Row_Warnings"
                in headers
            ):

                warning_col = (
                    headers.index(
                        "Row_Warnings"
                    )
                    + 1
                )

                for row in range(
                    2,
                    sheet.max_row + 1
                ):

                    cell = sheet.cell(
                        row=row,
                        column=warning_col
                    )

                    if cell.value:

                        cell.fill = (
                            warning_fill
                        )

            if (
                "Strong_Issues"
                in headers
            ):

                strong_col = (
                    headers.index(
                        "Strong_Issues"
                    )
                    + 1
                )

                for row in range(
                    2,
                    sheet.max_row + 1
                ):

                    cell = sheet.cell(
                        row=row,
                        column=strong_col
                    )

                    if cell.value:

                        cell.fill = (
                            strong_fill
                        )

        workbook.save(
            filename
        )

    # ========================================================
    # CREATE TEMPLATE
    # ========================================================

    def create_template(self):

        filename = filedialog.asksaveasfilename(
            title="Create empty Excel template",

            defaultextension=".xlsx",

            filetypes=[
                (
                    "Excel files",
                    "*.xlsx"
                )
            ],
        )

        if not filename:
            return

        try:

            template_columns = [
                "tree id",
                "length in m",
                "diameter in cm",
                "age in years",
                "Count_Knots",
                "Knot_Diameter_mm",
                "Count_Cracks",
                "Crack_Length_cm",
                "Crack_Width_mm",
                "Has_Forking",
                "Has_Bend",
                "Has_Disease",
            ]

            template_df = pd.DataFrame(
                columns=template_columns
            )

            dictionary_df = (
                create_data_dictionary()
            )

            with pd.ExcelWriter(
                filename,
                engine="openpyxl"
            ) as writer:

                template_df.to_excel(
                    writer,
                    sheet_name="Input Data",
                    index=False
                )

                dictionary_df.to_excel(
                    writer,
                    sheet_name="Data_Dictionary",
                    index=False
                )

            self.format_saved_workbook(
                filename
            )

            messagebox.showinfo(
                "Template Created",

                "Empty Excel template created:"
                "\n\n"
                f"{filename}"
            )

        except Exception as exc:

            messagebox.showerror(
                "Template Error",

                "Could not create the Excel template:"
                "\n\n"
                f"{type(exc).__name__}: {exc}"
            )

    # ========================================================
    # BAR CHART
    # ========================================================

    def show_bar_chart(self):

        if self.df is None:

            messagebox.showwarning(
                "No Data",
                "Please load and evaluate data first."
            )

            return

        if (
            "Quality_Class"
            not in self.df.columns
        ):

            messagebox.showwarning(
                "No Evaluation",
                "Please run evaluation first."
            )

            return

        counts = (
            self.df[
                "Quality_Class"
            ]
            .value_counts()
            .reindex(
                [
                    "High",
                    "Medium",
                    "Low",
                    "Very Low",
                ],
                fill_value=0
            )
        )

        chart_window = tk.Toplevel(
            self.root
        )

        chart_window.title(
            "Quality Class Distribution"
        )

        chart_window.geometry(
            "800x600"
        )

        figure = plt.Figure(
            figsize=(8, 5),
            dpi=100
        )

        axis = figure.add_subplot(
            111
        )

        axis.bar(
            counts.index,
            counts.values
        )

        axis.set_title(
            "Forest Log Quality Distribution"
        )

        axis.set_xlabel(
            "Quality Class"
        )

        axis.set_ylabel(
            "Number of Logs"
        )

        axis.tick_params(
            axis="x",
            rotation=20
        )

        figure.tight_layout()

        canvas = (
            FigureCanvasTkAgg(
                figure,
                master=chart_window
            )
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

    # ========================================================
    # PIE CHART
    # ========================================================

    def show_pie_chart(self):

        if self.df is None:

            messagebox.showwarning(
                "No Data",
                "Please load and evaluate data first."
            )

            return

        if (
            "Quality_Class"
            not in self.df.columns
        ):

            messagebox.showwarning(
                "No Evaluation",
                "Please run evaluation first."
            )

            return

        counts = (
            self.df[
                "Quality_Class"
            ]
            .value_counts()
            .reindex(
                [
                    "High",
                    "Medium",
                    "Low",
                    "Very Low",
                ],
                fill_value=0
            )
        )

        counts = counts[
            counts > 0
        ]

        chart_window = tk.Toplevel(
            self.root
        )

        chart_window.title(
            "Quality Class Pie Chart"
        )

        chart_window.geometry(
            "800x600"
        )

        figure = plt.Figure(
            figsize=(8, 5),
            dpi=100
        )

        axis = figure.add_subplot(
            111
        )

        axis.pie(
            counts.values,
            labels=counts.index,
            autopct="%1.1f%%",
            startangle=90
        )

        axis.set_title(
            "Forest Log Quality Distribution"
        )

        figure.tight_layout()

        canvas = (
            FigureCanvasTkAgg(
                figure,
                master=chart_window
            )
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )


# ============================================================
# START APPLICATION
# ============================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = ForestQualityApp(
        root
    )

    root.mainloop()
