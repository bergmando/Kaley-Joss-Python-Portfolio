# -*- coding: utf-8 -*-
"""

This file is my code solution for the following task. It demonstrates skills 
in document parsing, creating HTML parser functions, bing API websearches 
and SQL database storing.

This was completed Jul 2023, in ~11 hours of time.

I did not have experience with HTML, webscraping, the bing API or SQL before this 
task. I learned it for the task.

(For reference:
In the CSV file (“RA_test.csv”) exists a table containing the following information for the
Form D filing of 6 private equity investment firms:
-	Name of the firm: “groupname”
-	Type of filing: “submissiontype”
-	Unique fund identifier: “CIK”
-	Link to the groups website: “URL to Team Page”
-	A link to a text file that contains the full submission on the EDGAR website: “link”)

Based on this information, please write a Python program to carry out the following steps:
1)	Access the CSV file.
2)	Use the provided links to fetch the six Form D filings directly from the EDGAR website.
3)	Create a basic text parser that, for each file:
a.	Extracts the HTML header.
b.	Extracts the company name, submission type, and date of filing from the header.
c.	Prints output indicating which file is being processed and verify whether the data extracted from the header matches the information in the CSV file.
4)	Add a function to search for the fund’s website using the information in the Form D filing (e.g., a python script using the Bing or similar search engine).
5)	Construct an SQL table to store all the fund information (groupname, submissiontype, filingdate, website, and full text of the Form D).  That is, provide the necessary SQL statements to create and store the data. 


Original file is located at
    https://colab.research.google.com/drive/1pKHPDhlY1hzeJeB0XqTBTwp7Z5H8i759
"""

from google.colab import drive
drive.mount('/content/drive')

import os

new_directory = "/content/drive/MyDrive/"
os.chdir(new_directory)

os.getcwd() #this asks: where am I? Will return filepath (to check)

import pandas as pd
import requests

import csv
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin




#Create function to read in the CSV file as a list of lists
def read_csv_file(file_path):
    try:
        with open(file_path, 'r') as file:
            reader = csv.reader(file)
            data = [row for row in reader]  # Read all rows and store them in a list
            return data
    except FileNotFoundError:
        print("File not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

#Create a function to cycle through the links in the csv_data and fetch the form D filings links
def fetch_html(x):
  a = csv_data[x][4]
  return a

#Create a function to fetch the actual HTML content from the links
def get_html_content(url):
    try:
        response = requests.get(url)
        if response.ok:
            return response.text
        else:
            print(f"Failed to fetch HTML content from {url}. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching HTML content from {url}: {e}")
        return None

#Create a function that parses the text content from the HTML link
def parse_text_content(text_content):

    #HTML header
    header_tag = text_content.find('head')
    if header_tag:
      header = header_tag.text.strip()
    #  print(header)
    else:
      header_tag = text_content.find('SEC-HEADER')
      if header_tag:
        header = header_tag.text.strip()
    # print(header)


    #Company name
    company_name_tag = text_content.find('entityname')
    if company_name_tag:
      company_name = company_name_tag.text.strip() if company_name_tag else "Not found"
      print(f"Company Name: {company_name}")
      data_list[1].append(company_name)
    else:
      name_parent = text_content.find('th', class_="FormText", string='Name of Issuer')
      if name_parent:
        table_row = name_parent.find_parent('tr')
        company_name_tag = table_row.find_next('td', class_="FormData")
        if company_name_tag:
          company_name = company_name_tag.text.strip()
          print(f"Company Name: {company_name}")
          data_list[1].append(company_name)
        else:
          print("Company Name was not found as the sibling to Name of Issuer")
      else:
        print("Name of Issuer header was not found")



    #Submission type
    text_to_strip = 'SEC FORM'
    sub_type_tag = text_content.find('submissiontype')
    if sub_type_tag:
      sub_type = sub_type_tag.text.strip() if sub_type_tag else "Not found in submissiontype"
      print(f"Submission Type: {sub_type}")
      data_list[3].append(sub_type)
    else:
      sub_type_tag = text_content.find('title')
      if sub_type_tag:
        sub_type = sub_type_tag.text.strip() if sub_type_tag else "Not found in title"
        if sub_type.find(text_to_strip) != -1:
          sub_type = sub_type.replace(text_to_strip, "")
          print(f"Submission Type: {sub_type}")
          data_list[3].append(sub_type)
        else:
          print(f"Submission Type: {sub_type}")
          data_list[3].append(sub_type)


    #Date of filing -- ASSUMING: Signature Date is the date of filing, since no other date is listed
    gparent_tag = text_content.find('signature')
    if gparent_tag:
      date_of_filing_tag = gparent_tag.find('signaturedate')
      if date_of_filing_tag:
          date_of_filing = date_of_filing_tag.text.strip()
          print(f"Date of Filing: {date_of_filing}")
          data_list[4].append(date_of_filing)
    else:
      dof_parent = text_content.find('table', attrs={'summary': 'Signature Block'})
      if dof_parent:
        td_tags = dof_parent.find_all('td')
        dof_child = td_tags[4]
        if dof_child:
          date_of_filing = dof_child.text.strip()
          print(f"Date of Filing: {date_of_filing}")
          data_list[4].append(date_of_filing)
        else:
          print("- Not found, though Signature Block exists")
      else:
        print("Not found, neither signature block or signatureDate exist")








##Main Program##

# Read in the file RA_test.csv
file_path = "/content/drive/MyDrive/RA_test.csv"

if os.path.isfile(file_path):
    csv_data = read_csv_file(file_path)

# Create data_list, so that data pulled from the HTML site can be appended to SQL database
data_list = []
data_list.append(["CIK"]) 0
data_list.append(["groupname"]) 1
data_list.append(["URL"]) 2
data_list.append(["submissiontype"]) 3
data_list.append(["submissiondate"]) 4


#Create a function that uses the links provided to fetch the Form D filing info directly from the EDGAR website, aka 'link' column
headers = {'User-Agent': 'Mozilla/5.0'}
for x in range(len(csv_data)):
  try:
    response = requests.get(csv_data[x][4], headers=headers) #use the url from each line of the csv file
    if response.ok:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser') #save the html string as a BeautifulSoup nested data structure
        company_name = csv_data[x][0] #company name from CSV
        print("For company " + company_name + ":")
        parse_text_content(soup) #run the HTML webscraper
        #if csv_data[x][0] == company_name and csv_data[x][1] == sub_type:
        #  print("Is scraped data equal to CSV data: YES")
        print(csv_data[x][4]) #print the weblink
        print("")
        print("")
    else:
        print(f"Failed to fetch content from {csv_data[x][4]}. Status code: {response.status_code}")
  except requests.exceptions.RequestException as e:
    print(f"An error occurred while fetching content from {csv_data[x][4]}: {e}")

# Create function to use the fund data to search Bing
# I know this is not what the question asked, but I don't know how to search a specific website, so I did this instead
subscription_key = "562f7fd1f3b848fa998061a70ac829e9"
assert subscription_key
search_url = "https://api.bing.microsoft.com/v7.0/search"
import requests

for x in range(1,6):
  search_term = csv_data[x][3]
  headers = {"Ocp-Apim-Subscription-Key": subscription_key}
  params = {"q": search_term, "textDecorations": True, "textFormat": "HTML"}
  response = requests.get(search_url, headers=headers, params=params)
  response.raise_for_status()
  search_results = response.json()
  print(csv_data[x][0])
  from IPython.display import HTML

  rows = "\n".join(["""<tr>
                        <td><a href=\"{0}\">{1}</a></td>
                        <td>{2}</td>
                      </tr>""".format(v["url"], v["name"], v["snippet"])
                    for v in search_results["webPages"]["value"]])
  display(HTML("<table>{0}</table>".format(rows)))
  print("")
  print("")


#Storing SQL Data
# I cannot actually use SQL database because I don't have a subscription and its $372/month to make a basic sql database in Microsoft Azure, as I understand
# I can't find another way to connect to a database/find a database

!pip install pg8000
import pg8000
host = 'localhost'
port = 5432
database = 'your_database_name'
user = 'Kaley Joss'
password = '949baba'

#Connect to the database
conn = pg8000.connect(
    host=host,
    port=port,
    database=database,
    user=user,
    password=password
)

# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Define the SQL query to create the table
create_table_query = """
CREATE TABLE IF NOT EXISTS FormD_Filings (
    CIK SERIAL PRIMARY KEY,
    groupname VARCHAR(255),
    URL VARCHAR(255),
    submissiontype VARCHAR(255),
    submissiondate VARCHAR(255),
)
"""

# Execute the SQL query to create the table
cursor.execute(create_table_query)

#Make a data insert query
insert_query = """
INSERT INTO FormD_Filings (CIK, groupname, "URL to Team Page")
VALUES (%s, %s, %s)
"""

#Insert the data
try:
    # Loop through the data_list and execute the INSERT query for each set of values
    for data in data_list:
        cursor.execute(insert_query, data)

    # Commit the changes to the database
    conn.commit()

    print("Data inserted successfully!")
except requests.exceptions.RequestException as e:
    print(f"An error occurred while inserting data: {e}")


# Commit the changes to the database
conn.commit()

# Close the cursor and the connection
cursor.close()
conn.close()
