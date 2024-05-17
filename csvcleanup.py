<<<<<<< HEAD
import csv
import json
import os

# Define a dictionary to map subsection codes to organization types
organization_types = {
    "1": "Corporations organized under Act of Congress (including Federal Credit Unions)",
    "2": "Title-Holding Corporations for Exempt Organizations",
    "3": "Charitable Organizations (501(c)(3))",
    "4": "Social Welfare Organizations (501(c)(4))",
    "5": "Labor, Agricultural, and Horticultural Organizations (501(c)(5))",
    "6": "Business Leagues, Chambers of Commerce, Real Estate Boards, etc. (501(c)(6))",
    "7": "Social and Recreation Clubs (501(c)(7))",
    "8": "Fraternal Beneficiary Societies and Associations (501(c)(8))",
    "9": "Voluntary Employees' Beneficiary Associations (501(c)(9))",
    "10": "Domestic Fraternal Societies and Associations (501(c)(10))",
    "11": "Teachers' Retirement Fund Associations (501(c)(11))",
    "12": "Benevolent Life Insurance Associations, Mutual Ditch or Irrigation Companies, Mutual or Cooperative Telephone Companies, etc. (501(c)(12))",
    "13": "Cemetery Companies (501(c)(13))",
    "14": "State-Chartered Credit Unions, Mutual Reserve Funds (501(c)(14))",
    "15": "Mutual Insurance Companies or Associations (501(c)(15))",
    "16": "Cooperative Organizations to Finance Crop Operations (501(c)(16))",
    "17": "Supplemental Unemployment Benefit Trusts (501(c)(17))",
    "18": "Employee Funded Pension Trust (created before June 25, 1959) (501(c)(18))",
    "19": "Post or Organization of Past or Present Members of the Armed Forces (501(c)(19))",
    "20": "Group Legal Services Plan Organizations (501(c)(20))",
    "21": "Black Lung Benefit Trusts (501(c)(21))",
    "22": "Withdrawal Liability Payment Fund (501(c)(22))",
    "23": "Veterans Organization (501(c)(23))",
    "24": "Section 4049 ERISA Trusts (501(c)(24))",
    "25": "Title Holding Corporations or Trusts with Multiple Parents (501(c)(25))",
    "26": "State-Sponsored Organization Providing Health Coverage for High-Risk Individuals (501(c)(26))",
    "27": "State-Sponsored Workers' Compensation Reinsurance Organization (501(c)(27))",
    "28": "National Railroad Retirement Investment Trust (501(c)(28))",
    "29": "Qualified Nonprofit Health Insurance Issuers (501(c)(29))",
    "30": "Political Organizations (527)"
}

# Function to read CSV file, map subsection codes to organization types, and save to a new CSV file
def map_and_save_organization_types(input_csv, output_csv):
    with open(input_csv, 'r') as infile, open(output_csv, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['Organization Type']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            subsection_code = row['SUBSECCD']
            organization_type = organization_types.get(subsection_code, "Unknown")
            row['Organization Type'] = organization_type
            writer.writerow(row)

# Define column header mappings
column_headers_mapping = {
    "EIN": "Employer Identification Number",
    "SEC_NAME": "Secondary Name",
    "FRCD": "Foundation Code",
    "SUBSECCD": "Subsection Code",
    "TAXPER": "Tax Period",
    "ASSETS": "Total Assets",
    "INCOME": "Total Income",
    "NAME": "Organization Name",
    "ADDRESS": "Address",
    "CITY": "City",
    "STATE": "State",
    "NTEEFINAL": "Final Return Indicator",
    "NAICS": "North American Industry Classification System (NAICS) Code",
    "ZIP5": "ZIP Code",
    "RULEDATE": "Ruling Date",
    "FIPS": "Federal Information Processing Standards (FIPS) Code",
    "FNDNCD": "Foundation Code",
    "PMSA": "Primary Metropolitan Statistical Area (PMSA) Code",
    "MSA_NECH": "Metropolitan Statistical Area (MSA) / New England City and Town Area (NECTA) Code",
    "CASSETS": "Current Assets",
    "CFINSRC": "Current Financial Source",
    "CTAXPER": "Current Tax Period",
    "CTOTREV": "Current Total Revenue",
    "ACCPER": "Accounting Period",
    "RANDNUM": "Random Number",
    "NTEECC": "National Taxonomy of Exempt Entities (NTEE) Core Code",
    "NTEE1": "NTEE-1 Code",
    "LEVEL4": "Level 4",
    "LEVEL1": "Level 1",
    "NTMAJ10": "NTEE Major Group 10",
    "MAJGRPB": "Major Group B",
    "LEVEL3": "Level 3",
    "LEVEL2": "Level 2",
    "NTMAJ12": "NTEE Major Group 12",
    "NTMAJ5": "NTEE Major Group 5",
    "FILER": "Filer",
    "ZFILER": "Z-Filer",
    "OUTREAS": "Outreason",
    "OUTNCCS": "Out Nonprofit Organization's Reason",
    "Organization Type": "Organization Type"
}

# Convert CSV file to JSON format
def convert_csv_to_json(input_csv):
    json_data = []
    with open(input_csv, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            renamed_row = {column_headers_mapping[col]: value for col, value in row.items()}
            json_data.append(renamed_row)
    return json_data

# Split JSON data into multiple files based on ZIP code
def split_json_by_zipcode(json_data, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create a dictionary to store file writers for each unique ZIP code
    zip_file_writers = {}

    for row in json_data:
        zipcode = row['ZIP Code']
        if zipcode not in zip_file_writers:
            # Create a new JSON file for the ZIP code in the output folder
            output_json = os.path.join(output_folder, f"{zipcode}_data.json")
            zip_file_writers[zipcode] = open(output_json, 'w', encoding='utf-8')
            json.dump([row], zip_file_writers[zipcode], ensure_ascii=False, indent=4)
        else:
            json.dump(row, zip_file_writers[zipcode], ensure_ascii=False, indent=4)
            zip_file_writers[zipcode].write('\n')

    # Close all file writers
    for writer in zip_file_writers.values():
        writer.close()

# Paths to input CSV file and output folder
input_csv_file = r'C:\Users\Megha Patel\Downloads\zips_BMF-2022-08-501CX-NONPROFIT-PX.csv'
output_csv_file = r'C:\Users\Megha Patel\Documents\mapped_organizations.csv'
output_folder = r'C:\Users\Megha Patel\Documents\Split_By_Zipcode_JSON'

# Call the function to map organization types and save to a new CSV file
map_and_save_organization_types(input_csv_file, output_csv_file)

# Convert CSV to JSON
json_data = convert_csv_to_json(output_csv_file)

# Split JSON by ZIP code
split_json_by_zipcode(json_data, output_folder)
=======
import csv
import json
import os

# Define a dictionary to map subsection codes to organization types
organization_types = {
    "1": "Corporations organized under Act of Congress (including Federal Credit Unions)",
    "2": "Title-Holding Corporations for Exempt Organizations",
    "3": "Charitable Organizations (501(c)(3))",
    "4": "Social Welfare Organizations (501(c)(4))",
    "5": "Labor, Agricultural, and Horticultural Organizations (501(c)(5))",
    "6": "Business Leagues, Chambers of Commerce, Real Estate Boards, etc. (501(c)(6))",
    "7": "Social and Recreation Clubs (501(c)(7))",
    "8": "Fraternal Beneficiary Societies and Associations (501(c)(8))",
    "9": "Voluntary Employees' Beneficiary Associations (501(c)(9))",
    "10": "Domestic Fraternal Societies and Associations (501(c)(10))",
    "11": "Teachers' Retirement Fund Associations (501(c)(11))",
    "12": "Benevolent Life Insurance Associations, Mutual Ditch or Irrigation Companies, Mutual or Cooperative Telephone Companies, etc. (501(c)(12))",
    "13": "Cemetery Companies (501(c)(13))",
    "14": "State-Chartered Credit Unions, Mutual Reserve Funds (501(c)(14))",
    "15": "Mutual Insurance Companies or Associations (501(c)(15))",
    "16": "Cooperative Organizations to Finance Crop Operations (501(c)(16))",
    "17": "Supplemental Unemployment Benefit Trusts (501(c)(17))",
    "18": "Employee Funded Pension Trust (created before June 25, 1959) (501(c)(18))",
    "19": "Post or Organization of Past or Present Members of the Armed Forces (501(c)(19))",
    "20": "Group Legal Services Plan Organizations (501(c)(20))",
    "21": "Black Lung Benefit Trusts (501(c)(21))",
    "22": "Withdrawal Liability Payment Fund (501(c)(22))",
    "23": "Veterans Organization (501(c)(23))",
    "24": "Section 4049 ERISA Trusts (501(c)(24))",
    "25": "Title Holding Corporations or Trusts with Multiple Parents (501(c)(25))",
    "26": "State-Sponsored Organization Providing Health Coverage for High-Risk Individuals (501(c)(26))",
    "27": "State-Sponsored Workers' Compensation Reinsurance Organization (501(c)(27))",
    "28": "National Railroad Retirement Investment Trust (501(c)(28))",
    "29": "Qualified Nonprofit Health Insurance Issuers (501(c)(29))",
    "30": "Political Organizations (527)"
}

# Function to read CSV file, map subsection codes to organization types, and save to a new CSV file
def map_and_save_organization_types(input_csv, output_csv):
    with open(input_csv, 'r') as infile, open(output_csv, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['Organization Type']
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            subsection_code = row['SUBSECCD']
            organization_type = organization_types.get(subsection_code, "Unknown")
            row['Organization Type'] = organization_type
            writer.writerow(row)

# Define column header mappings
column_headers_mapping = {
    "EIN": "Employer Identification Number",
    "SEC_NAME": "Secondary Name",
    "FRCD": "Foundation Code",
    "SUBSECCD": "Subsection Code",
    "TAXPER": "Tax Period",
    "ASSETS": "Total Assets",
    "INCOME": "Total Income",
    "NAME": "Organization Name",
    "ADDRESS": "Address",
    "CITY": "City",
    "STATE": "State",
    "NTEEFINAL": "Final Return Indicator",
    "NAICS": "North American Industry Classification System (NAICS) Code",
    "ZIP5": "ZIP Code",
    "RULEDATE": "Ruling Date",
    "FIPS": "Federal Information Processing Standards (FIPS) Code",
    "FNDNCD": "Foundation Code",
    "PMSA": "Primary Metropolitan Statistical Area (PMSA) Code",
    "MSA_NECH": "Metropolitan Statistical Area (MSA) / New England City and Town Area (NECTA) Code",
    "CASSETS": "Current Assets",
    "CFINSRC": "Current Financial Source",
    "CTAXPER": "Current Tax Period",
    "CTOTREV": "Current Total Revenue",
    "ACCPER": "Accounting Period",
    "RANDNUM": "Random Number",
    "NTEECC": "National Taxonomy of Exempt Entities (NTEE) Core Code",
    "NTEE1": "NTEE-1 Code",
    "LEVEL4": "Level 4",
    "LEVEL1": "Level 1",
    "NTMAJ10": "NTEE Major Group 10",
    "MAJGRPB": "Major Group B",
    "LEVEL3": "Level 3",
    "LEVEL2": "Level 2",
    "NTMAJ12": "NTEE Major Group 12",
    "NTMAJ5": "NTEE Major Group 5",
    "FILER": "Filer",
    "ZFILER": "Z-Filer",
    "OUTREAS": "Outreason",
    "OUTNCCS": "Out Nonprofit Organization's Reason",
    "Organization Type": "Organization Type"
}

# Convert CSV file to JSON format
def convert_csv_to_json(input_csv):
    json_data = []
    with open(input_csv, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            renamed_row = {column_headers_mapping[col]: value for col, value in row.items()}
            json_data.append(renamed_row)
    return json_data

# Split JSON data into multiple files based on ZIP code
def split_json_by_zipcode(json_data, output_folder):
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create a dictionary to store file writers for each unique ZIP code
    zip_file_writers = {}

    for row in json_data:
        zipcode = row['ZIP Code']
        if zipcode not in zip_file_writers:
            # Create a new JSON file for the ZIP code in the output folder
            output_json = os.path.join(output_folder, f"{zipcode}_data.json")
            zip_file_writers[zipcode] = open(output_json, 'w', encoding='utf-8')
            json.dump([row], zip_file_writers[zipcode], ensure_ascii=False, indent=4)
        else:
            json.dump(row, zip_file_writers[zipcode], ensure_ascii=False, indent=4)
            zip_file_writers[zipcode].write('\n')

    # Close all file writers
    for writer in zip_file_writers.values():
        writer.close()

# Paths to input CSV file and output folder
input_csv_file = r'C:\Users\Megha Patel\Downloads\zips_BMF-2022-08-501CX-NONPROFIT-PX.csv'
output_csv_file = r'C:\Users\Megha Patel\Documents\mapped_organizations.csv'
output_folder = r'C:\Users\Megha Patel\Documents\Split_By_Zipcode_JSON'

# Call the function to map organization types and save to a new CSV file
map_and_save_organization_types(input_csv_file, output_csv_file)

# Convert CSV to JSON
json_data = convert_csv_to_json(output_csv_file)

# Split JSON by ZIP code
split_json_by_zipcode(json_data, output_folder)
>>>>>>> c371ee9210c5111d439b1bd1b7c04dd3ec58b61b
