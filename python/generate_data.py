import argparse
from faker import Faker
import numpy as np
import csv

def generate_fake_companies( num_companies, fake ):
   companies = []
   for ii in range( num_companies ):
      companies.append( fake.company() )
   return companies

def generate_contact( companies, fake ):
   contact = []
   name = fake.name().split(" ")
   fname = name[0]
   lname = name[-1]
   if ( len(name) > 2 ):
      fname = " ".join(name[0:-2])
   email        = fake.email()
   company      = companies[np.random.randint(0, len(companies) )]
   position     = fake.job()
   date         = fake.date()
   return [ fname, lname, email, company, position, date ]


def main():
   parser = argparse.ArgumentParser()
   parser.add_argument("csv_fname",
                        help="Output a CSV file that is the same format as \
                              Connections.csv from LinkedIn",
                        type=str)
   parser.add_argument("--num_contacts",
                        help="Number of Contacts",
                        default=100,
                        type=int)
   parser.add_argument("--num_companies",
                        help="Number of Companies",
                        default=20,
                        type=int)
   args = parser.parse_args()

   # Generate fake companies
   fake = Faker()
   companies = generate_fake_companies( args.num_companies, fake )

   fields = ['First Name',
             'Last Name',
             'Email Address',
             'Company',
             'Position',
             'Connected On']

   contacts = []
   for ii in range( args.num_contacts ):
      contacts.append( generate_contact( companies, fake ))

   with open( args.csv_fname, 'w' ) as csvfile:
      # First 3 rows are not used
      csvwriter = csv.writer(csvfile)
      csvwriter.writerows( [[],[],[]])
      csvwriter.writerow( fields )
      csvwriter.writerows( contacts )

if __name__ == "__main__":
   main()

