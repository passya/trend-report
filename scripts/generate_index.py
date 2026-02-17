import os
import json
import re

REPORTS_DIR = 'docs/reports'
OUTPUT_FILE = 'docs/reports.json'

def generate_index():
    reports = []
    
    # Ensure directory exists
    if not os.path.exists(REPORTS_DIR):
        print(f"Directory {REPORTS_DIR} not found.")
        return

    # Scan for markdown files
    for filename in os.listdir(REPORTS_DIR):
        if filename.endswith('.md'):
            filepath = os.path.join(REPORTS_DIR, filename)
            
            # Extract date from filename (trend_analysis_YYYY-MM-DD.md)
            date_match = re.search(r'trend_analysis_(\d{4}-\d{2}-\d{2})', filename)
            date = date_match.group(1) if date_match else "Unknown Date"
            
            # Extract title (first h1)
            title = "Daily Trend Analysis"
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('# '):
                            title = line.strip('# ').strip()
                            break
            except Exception as e:
                print(f"Error reading {filename}: {e}")

            reports.append({
                'filename': filename,
                'date': date,
                'title': title
            })

    # Sort by date descending
    reports.sort(key=lambda x: x['date'], reverse=True)

    # Write to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(reports, f, indent=2, ensure_ascii=False)
    
    print(f"Successfully indexed {len(reports)} reports to {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_index()
