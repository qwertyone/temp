import pandas as pd
from fpdf import FPDF
import openai
import time
import os
import re
import random

openai.api_key = ""


def open_file(file_path):
    """Load a CSV or Excel file into a pandas DataFrame."""
    try:
        if file_path.endswith(".csv"):
            return pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file_path)
        else:
            raise ValueError("Unsupported file format")
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return None

def mark_duplicates(df):
    """Identify duplicate rows and add a new column 'Is_Duplicate'."""
    df['Is_Duplicate'] = df.duplicated(keep=False)
    return df

def mark_exclusions(df, excluded_products_file, excluded_manufacturers_file):
    """Identify excluded products and manufacturers."""
    try:
        excluded_products = pd.read_csv(excluded_products_file)['Excluded_Products'].dropna().astype(str).tolist()
        excluded_manufacturers = pd.read_csv(excluded_manufacturers_file)['Excluded_Manufacturers'].dropna().astype(str).tolist()

        df['Is_Excluded_Product'] = df[' Brand Name'].astype(str).isin(excluded_products)
        df['Is_Excluded_Manufacturer'] = df['Manufacturer'].astype(str).isin(excluded_manufacturers)
        df['Is_Robust_Duplicate_Helper'] = df['Event Date'].astype(str) + df['Event Text'].astype(str)
        df['Is_Robust_Duplicate'] = df['Is_Robust_Duplicate_Helper'].duplicated(keep=False)
    except Exception as e:
        print(f"Error processing exclusions: {e}")
    return df

def generate_statistics(df):
    """Compute statistics for excluded and duplicate rows."""
    total_rows = len(df)
    columns_to_check = ['Is_Duplicate', 'Is_Excluded_Product', 'Is_Excluded_Manufacturer', 'Is_Robust_Duplicate']
    total_dropped = df[columns_to_check].any(axis=1).sum()
    total_considered = total_rows - total_dropped
    return total_considered, total_dropped, total_rows, df[columns_to_check].describe()

def generate_pdf_report(total_considered, total_rows, total_dropped, stats, output_pdf, file_year):
    """Generate a PDF report with statistics."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16, style='B')

    # Title
    pdf.cell(200, 10, txt= "Data Analysis Report " + file_year, ln=True, align='C')

    # Excluded products summary
    pdf.output(output_pdf)

def parse_response(response_text):
    """Extract classification and reasoning using regex."""
    match = re.search(r'\*\*Classification\*\*:\s*(.*?)\s*\*\*Reasoning\*\*:\s*(.*)', response_text, re.DOTALL)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return "Error", "Unexpected response format"

def classify_event_with_llm(event_text, hazard_classifications_file):
    """Classify event using OpenAI's model."""
    hazard_data = pd.read_csv(hazard_classifications_file)
    hazardous_situations = hazard_data['Hazardous Situation'].tolist()
    definitions = hazard_data['Definition-Description'].tolist()
    
    prompt = f"""
    Classify the following medical device event. Validate the classification to definition:
    **Event**: {event_text}
    
    **Categories**: {hazardous_situations}
    
    **Definitions**: {definitions}
    
    **Format**:
    **Classification**: [Category]  
    **Reasoning**: [Justification]
    """
    
    retries = 1
    for i in range(retries):
        try:
            response = openai.chat.completions.create(  # 
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2
            )

            response_text = response["choices"][0]["message"]["content"]
            return parse_response(response_text)  #
        
        except openai.RateLimitError:
            wait_time = 5 * (2 ** i) + random.uniform(0, 1) 
            print(f"Rate limit hit. Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)

        except Exception as e:
            return "Error", f"Exception: {str(e)}"

    return "Error", "Max retries exceeded"

def apply_llm_classification(df, hazard_classifications_file):
    """Apply LLM classification to each row safely."""
    
    def classify_row(row):
        """Classify event if it passes all exclusion checks."""
        if row[['Is_Duplicate', 'Is_Excluded_Product', 'Is_Excluded_Manufacturer', 'Is_Robust_Duplicate']].any():
            return "Skipped", "Row excluded"
        return classify_event_with_llm(row["Event Text"], hazard_classifications_file)

    results = df.apply(classify_row, axis=1)
    df["Classification"], df["Reasoning"] = zip(*results)
    
    return df

def save_file(df, output_file):
    """Save the updated DataFrame."""
    if output_file.endswith(".csv"):
        df.to_csv(output_file, index=False)
    else:
        df.to_excel(output_file, index=False, engine='openpyxl')

def main(input_file, excluded_products_file, excluded_manufacturers_file, hazard_classifications_file, output_pdf, output_file, file_year):
    df = open_file(input_file)
    if df is None:
        return
    df = mark_duplicates(df)
    df = mark_exclusions(df, excluded_products_file, excluded_manufacturers_file)
    total_considered, total_dropped, total_rows, stats = generate_statistics(df)
    generate_pdf_report(total_considered, total_rows, total_dropped, stats, output_pdf, file_year)
    df = apply_llm_classification(df, hazard_classifications_file)
    save_file(df, output_file)
    print(f"Processed data saved to {output_file} and report generated at {output_pdf}.")

# File paths
file_year = "2024"
input_file = "maude_test.xlsx"
output_file = "maude_test_full.xlsx"
excluded_products_file = "Excluded_Products.csv"
excluded_manufacturers_file = "Excluded_Manufacturers.csv"
hazard_classifications_file = "HazardousClassificationReference.csv"
output_pdf = f"maude_SI_reports_{file_year}_analysis_report.pdf"



# Run the script
main(input_file, excluded_products_file, excluded_manufacturers_file, hazard_classifications_file, output_pdf, output_file, file_year)
