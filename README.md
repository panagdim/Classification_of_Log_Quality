🌲 About

This project is a Python-based application for log quality classification using forest inventory data. It processes datasets in CSV, Excel, or TXT format containing tree attributes such as:

Tree height
Diameter at Breast Height (DBH)
Defect indicators (e.g., knots, forking, cracks, diseases)

Based on these inputs, the application assigns a quality class to each log.

🧠 Classification Approach

This is a flexible, general-purpose classification tool. Since log quality standards vary across regions and countries, the system is designed to be easily adaptable:

Supports numerical classification systems (e.g., classes 1–7)
Supports categorical systems (e.g., Good / Medium / Low)
🛠️ Classification rules can be customized directly in the source code to match local forestry standards
📊 Included Test Data & Scripts

The repository includes three example Excel datasets along with their corresponding Python scripts:

Categorical Classification
📄 Dataset: Classification of log quality based on categorical data
🧪 Script: Classification of Log Quality Categorical.py

Numerical Classification
📄 Dataset: Classification of log quality based on numerical data
🧪 Script: Classification of Log Quality Numerical.py

Advanced Quality Assessment
📄 Dataset: Quality Assessment
🧪 Script: Advanced_Log_Classification.py
🌍 Application Domain

Forestry
Forest inventory analysis
Timber quality assessment

⚠️ Note

The provided datasets contain randomly generated data for testing and demonstration purposes only.

You are encouraged to:

Replace them with your own ground truth measurements
Adjust classification rules to better reflect real-world conditions
Validate and evaluate model performance using domain-specific data

Contributor: Dimitris Panagiotidis
