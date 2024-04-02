import csv

with open('../test-csv/credits.csv') as csv_file:
  csv_reader = csv.reader(csv_file)

  for entry in csv_reader:
    print(entry[0])