from bankmodules import Customer, Account

class DataSource:
    
    def __init__(self, fileName = "./database/database.txt"):
        self.fileName = fileName
        self.bankCustomerList = []
            
    def datasource_conn(self):
        if ".txt" in self.fileName:
            return self.connect_text_file()
        elif ".json" in self.fileName:
            return self.connect_json_file()
        elif ".xml" in self.fileName:
            return self.connect_xml_file()
        else:
            return False, f"Unsupported database format: {self.fileName}"

    def connect_json_file(self):
        return False, f"Not implemented yet, for: {self.fileName}"

    def connect_xml_file(self):
        return False, f"Not implemented yet, for: {self.fileName}"

    def connect_text_file(self):
        self.bankCustomerList = []
        try:
            with open(self.fileName, "r+") as f:
                for cstring in f:
                    self.bankCustomerList.append(self.parse_customer_string(cstring))    
        except Exception as ex:
            return False, f"Database {self.fileName} open error: {ex} "
    
        return True, f"Connection successful: {self.fileName}"

    def parse_customer_string(self, cstring):
        customer_data = cstring.split(":")
        iD = int(customer_data[0])
        name = str(customer_data[1])
        pn = int(customer_data[2])
        accounts = []                     
        for a in ":".join(customer_data[3:]).split("#"):
            accNumber = int(a.split(":")[0])
            accType = str(a.split(":")[1])
            accSaldo = float(a.split(":")[2])
            accounts.append(Account(saldo = accSaldo,
                accountType = accType, accountNumber = accNumber)) 
        return Customer(iD = iD, name = name,
                personalNumber = pn, accounts = accounts)

    def get_all(self):
        return self.bankCustomerList
    

    def find_by_id(self, iD):
        for c in self.bankCustomerList:
            if c.iD == iD:
                return c

    def remove_by_id(self, iD):
        found = None
        for c in self.bankCustomerList:
            if c.iD == iD:
                    self.bankCustomerList.remove(c) 
                    found = c
                    break
        if found != None:
            self.refresh_database()
            return found
        else:
            return -1        

    def refresh_database(self):
        if ".txt" in self.fileName:
            with open(self.fileName, "w") as f:
                for c in self.bankCustomerList:
                    f.write(self.buld_customer_string(c))                    
                
    def buld_customer_string(self, customer):
        accData = ""
        accNumber = 1
        for acc in customer.accounts:
            separator = ""
            if accNumber < len(customer.accounts):
                separator = "#"   
            accData += f"{acc.accountNumber}:{acc.accountType}:{acc.saldo:.2f}{separator}"
            accNumber +=1
        return f"{customer.iD}:{customer.name}:{customer.personalNumber}:{accData}\n"

