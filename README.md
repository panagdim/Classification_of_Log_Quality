🌲 Abstract 

This application is a desktop-based forestry log evaluation system designed to assess the quality of timber logs using a combination of physical attributes and defect analysis. It processes input data from Excel files containing log measurements such as length, diameter, and defect indicators (knots, cracks, forking, bending, and disease presence).

The system applies a non-linear scoring model that reflects realistic forestry behavior, where larger logs generally increase value while defects reduce quality through weighted penalties and interaction effects. The final output classifies each log into one of four quality categories: High, Medium, Low, or Very Low, and computes a normalized score out of 100.

The application also includes a graphical user interface (GUI) with a built-in dashboard that visualizes the distribution of log quality categories using a color-coded pie chart. Additionally, it generates a formatted Excel report with automatic column sizing and color-coded classification for easy interpretation and export.

⚠️ Note on Model Applicability

While the system provides a realistic and structured approximation of log quality evaluation, it is based on heuristic rules and engineered weights rather than certified forestry standards. Therefore, to achieve higher accuracy and real-world applicability, the model requires calibration using real or region-specific forestry data, including local grading standards, market pricing, and expert-validated log classifications.

Such calibration would allow the scoring system to better reflect regional forestry practices and commercial timber valuation systems, improving its reliability for operational or industrial use.

Contributor: Dimitris Panagiotidis
