import yaml

# Load metadata from YAML file
with open("geopolrisk-py/assessment/meta.yaml", "r") as file:
    metadata = yaml.safe_load(file)

# Accessing different parts of the metadata
tables = metadata.get("Tables", [])
regions_list = metadata.get("regionslist", {})
baci_codes = metadata.get("BACIcodes", {})
comtrade_codes = metadata.get("COMTRADEcodes", {})
output = metadata.get("Output", "")
database = metadata.get("Database", "")
baci_db = metadata.get("BACI", "")
output_folder = metadata.get("OutputFolder", "")

# Example usage:
print("Tables:", type(tables))
print("EU Countries:", type(regions_list))
print("BACI Codes for Indium:", type(baci_codes))
print("COMTRADE Codes for Indium:", type(comtrade_codes))
print("Output Database:", output)
print("Main Database:", database)
print("BACI Database:", baci_db)
print("Output Folder:", output_folder)
