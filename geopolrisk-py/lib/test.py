import sqlite3
import pandas as pd
from openpyxl import load_workbook

# Prompt the user for the Excel file path
excel_path = "Production.xlsx"

# Prompt the user for the SQLite database path
db_path = "test.db"

# Define the list of sheet names
sheet_names = [
    "Aluminium",
    "Antimony",
    "Asbestos",
    "Barytes",
    "Bismuth",
    "Cadmium",
    "Chromium",
    "Coal",
    "Cobalt",
    "Copper",
    "Gold",
    "Graphite",
    "Iron",
    "Lead",
    "Lithium",
    "Magnesite",
    "Magnesium",
    "Manganese",
    "Mercury",
    "Molybdenum",
    "Nickel",
    "Petroleum",
    "REE",
    "Silver",
    "Tin",
    "Titanium",
    "Tungsten",
    "Uranium",
    "Zinc",
    "Zirconium",
    "NG",
]

import pandas as pd
import sqlite3

def update_database(file_path, sheet_names, db_file_path):
    # Read the Excel file
    xl_file = pd.ExcelFile(file_path)
    
    # Create a connection to the SQLite database
    conn = sqlite3.connect(db_file_path)
    
    # Iterate over the sheets in the Excel file
    for sheet_name in sheet_names:
        # Read the sheet into a DataFrame
        df = pd.read_excel(xl_file, sheet_name)
        
        # Get the year column
        year_col = df.columns[0]
        
        # Get the country columns
        country_cols = df.columns[1:]
        
        # Create the table in the SQLite database
        cursor = conn.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS {sheet_name} (Country TEXT PRIMARY KEY, {', '.join(country_cols)});")
        
        # Get the current columns in the table
        cursor.execute(f"PRAGMA table_info({sheet_name})")
        existing_cols = [col[1] for col in cursor.fetchall()][1:]
        
        # Iterate over the rows in the DataFrame
        for index, row in df.iterrows():
            # Get the country and year
            country = row[0]
            
            # Check if the country already exists in the table
            cursor.execute(f"SELECT COUNT(*) FROM {sheet_name} WHERE Country=?", (country,))
            country_count = cursor.fetchone()[0]
            
            # If the country doesn't exist, insert a new row
            if country_count == 0:
                values = [country] + [None] * len(existing_cols)
                cursor.execute(f"INSERT INTO {sheet_name} VALUES ({', '.join(['?' for _ in range(len(values))])})", values)
                
            # Update the row with the new data
            for i, col in enumerate(country_cols):
                if col not in existing_cols:
                    # If the column doesn't exist, add it to the table
                    cursor.execute(f"ALTER TABLE {sheet_name} ADD COLUMN {col} REAL DEFAULT NULL;")
                    existing_cols.append(col)
                
                # Get the current value in the table
                cursor.execute(f"SELECT {col} FROM {sheet_name} WHERE Country=?", (country,))
                current_val = cursor.fetchone()[0]
                
                # Get the new value from the DataFrame
                new_val = row[col]
                
                # If the new value is different, update the row
                if current_val != new_val:
                    cursor.execute(f"UPDATE {sheet_name} SET {col}=? WHERE Country=?", (new_val, country))
        
        # Commit the changes to the database
        conn.commit()
        
    # Close the connection to the database
    conn.close()




update_database(excel_path, sheet_names, db_path)
