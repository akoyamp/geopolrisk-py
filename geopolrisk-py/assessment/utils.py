from .__init__ import logging
import yaml, sqlite3


def Load_Yaml(file_path):
    try:
        with open(file_path, "r") as meta_file:
            return yaml.safe_load(meta_file)
    except FileNotFoundError:
        logging.error("Yaml file not found.")
        return None


def execute_query(query, dbpath):
    conn = sqlite3.connect(dbpath)
    cursor = conn.cursor()
    is_select_query = query.strip().lower().startswith("select")
    if is_select_query:
        cursor.execute(query)
        results = cursor.fetchall()
    else:
        cursor.execute(query)
        results = None
    conn.commit()
    conn.close()
    if is_select_query:
        return results


def validate_country(regionlist: dict, countrylist: dict):
    pass
