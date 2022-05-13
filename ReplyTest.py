#!/usr/bin/env python
# coding: utf-8

from abc import ABC, abstractmethod
import csv
import re
 
class Encrypt(ABC):
    #These methods are applicable to all classes

    #Takes a row value as input and replaces alphanumeric values with X
    def replace_alphabets(self,row_value):
        return re.sub(r'[a-zA-Z]',r'X',row_value)

    #calculate average of Billing column values, handles invalid entries like $,£ etc.
    #If all the values are empty under Billing Column,replacing billing with average=1 in masked_clients.csv.
    def billing_average(self,billing_list,billing_sum = 0, billing_values_length = 0):
        numeric_billing_list = [i for i in billing_list if i.isnumeric()]
        if not numeric_billing_list:
            average = 1
        else:   
            for i in numeric_billing_list:
                billing_sum = billing_sum+float(i)
                billing_values_length+=1
            average = (billing_sum)/billing_values_length 
        return average  
    

#filepath: Path to input csv file
#filename: Destination csv filename to store results (encrypted data )       
class EncryptCSV(Encrypt):
    
#Takes csv file as input , reads the rows and replaces it with other values where necessary to provide encryption.
#filepath: Path to input csv file
#filename: Destination csv filename to store results (encrypted data )    
    def __init__(self,filepath,filename):
        super(EncryptCSV, self).__init__()
        self.filepath = filepath
        self.filename = filename
        #store encrypted values in temp_results and must be accessible to other functions in the class.
        self.temp_results = []
        #billing column data to calculate average.
        self.billing = []
        #names column data to dispaly Min,Max,Avg length of names.
        self.names = []
        
        #To store the records(rows of input csv file)
        temp_dicts = []
        try:
            with open(self.filepath) as f:
                records = csv.DictReader(f)
                temp_dicts = [x for x in records]
                try:
                    for row in temp_dicts: 
                        if not isinstance(row['Name'], str): #Name must be a string
                              raise TypeError("Name should be a string")
                        row['Name'] = super(EncryptCSV, self).replace_alphabets(row['Name'])
                        row['Email'] = super(EncryptCSV, self).replace_alphabets(row['Email'])
                        self.billing.append(row['Billing'])
                        self.names.append(row['Name'])
                        self.temp_results.append(row)
                except csv.Error as error:
                    raise ValueError(error)       
        except FileNotFoundError:
            print("File does not exist") 
            
            
    #write the data to output file with replaced values.       
    def replace_data(self):
        with open(self.filename,'w') as newfile:
             writer = csv.DictWriter(newfile, self.temp_results[0].keys())
             writer.writeheader()
             for data in self.temp_results:
                if data['Billing'] == ' ':
                    writer.writerow(data)
                    continue           
                data['Billing'] = super(EncryptCSV, self).billing_average(self.billing)
                writer.writerow(data) 
        print('Billing: Max. {}, Min. {},Avg. {}'.format(max(self.billing),min(self.billing),super(EncryptCSV, self).billing_average(self.billing)))                   
        name_lengths = [len(i) for i in self.names ]
        print('Name: Max. {}, Min. {},Avg. {}'.format(max(name_lengths),min(name_lengths),sum(name_lengths)/len(name_lengths)))

class EncryptDB(Encrypt):
    #sample sqlite Database methods
    def __init__(self, name):
        self._conn = sqlite3.connect(name)
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    def commit(self):
        self.connection.commit()

    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()

    def execute(self, sql, params=None):
        self.cursor.execute(sql, params or ())

    def fetchall(self):
        return self.cursor.fetchall()       


def main():
    #test1 is instance of EncryptCSV class and applying ".replace_data" method write encrypted data to output file.
    test1 = EncryptCSV('customers.csv','masked_clients.csv').replace_data()
    print('Encrytion process complete and result is saved to "masked_clients.csv" file')
    
if __name__ == '__main__':
    main()






