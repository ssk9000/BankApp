from bankmodules import Customer, Account, Transaction
class Bank:
    def __init__(self, name = "Fake Bank", dataSource = None):
        self.customers = []
        self.name = name
        self.dataSource = dataSource
        self.bankAccountFreeNumbers = [x for x in range(1001, 1201)] #max 200 account numbers
        self.bankCustomerIdsFree = [x for x in range(1, 101)]   #max 100 customer Ids
        self._load()

    def _load(self):
        if self.dataSource.datasource_conn()[0]:
            self.customers = self.dataSource.get_all()
        for c in self.customers:
            if c.iD in self.bankCustomerIdsFree:
                self.bankCustomerIdsFree.remove(c.iD)
                for a in c.accounts:
                    if a.accountNumber in self.bankAccountFreeNumbers:
                        self.bankAccountFreeNumbers.remove(a.accountNumber)

    def add_customer(self, name, personalNumber):
        if self._get_customer(personalNumber) != None:
            return False
        startAccount = Account(accountNumber = self.bankAccountFreeNumbers.pop(0)) #create start account for customer with zero amount
        customer = Customer(iD = self.bankCustomerIdsFree.pop(0),
                            name = name, personalNumber = personalNumber,
                            accounts = [startAccount])
        self.customers.append(customer)
        self.customers.sort(key = lambda c: c.iD) 
        self.dataSource.refresh_database()
        return True
        
    def get_customers(self):     
        customersInfo = []
        for c in self.customers:
            customersInfo.append((c.personalNumber, c.name, c.iD))   
        return customersInfo

    def _get_customer(self, personalNumber):
        for c in self.customers:
            if c.personalNumber == personalNumber:
                return c
        return None     

    def get_customer(self, personalNumber):
        for c in self.customers:
            if personalNumber == c.personalNumber:
                accountInfo = []
                for a in c.accounts:
                    accountInfo.append((a.accountNumber, a.accountType, a.saldo))
                return accountInfo
        return -1

    def change_customer_name(self, personalNumber, newName):
        for c in self.customers:
            if personalNumber == c.personalNumber:
                c.name = newName
                self.dataSource.refresh_database()
                return True
        return False

    def remove_customer(self, personalNumber):
        for c in self.customers:
            if personalNumber == c.personalNumber:
                self.bankCustomerIdsFree.append(c.iD)
                self.bankCustomerIdsFree.sort()
                moneyBack = 0
                accCloseReport = []
                accCloseReport.append((c.personalNumber, c.name)) #first turple customer data
                for a in c.accounts:
                    moneyBack += a.saldo
                    accCloseReport.append((a.accountNumber, 
                        a.accountType, a.saldo))    #append accounts info
                accCloseReport.append(moneyBack)    #last returned summa from closed accounts
                self.customers.remove(c)
                self.dataSource.refresh_database()
                return accCloseReport
        return -1

    def add_account(self,personalNumber):
        for c in self.customers:
            if personalNumber == c.personalNumber:
                number = self.bankAccountFreeNumbers.pop(0)
                c.accounts.append(Account(accountNumber = number))
                self.dataSource.refresh_database()
                return number
        return -1

    def _get_account(self, personalNumber, accountNumber):
        for c in self.customers:
            if personalNumber == c.personalNumber:
                for a in c.accounts:
                    if a.accountNumber == accountNumber:
                        return a
                return None
        return None
        
    def get_account(self, personalNumber, accountNumber):
        for c in self.customers:
            if personalNumber == c.personalNumber:
                for a in c.accounts:
                    if a.accountNumber == accountNumber:
                        return f"#Account Number:{a.accountNumber}, Account type: {a.accountType}, Saldo: {a.saldo}"
                return "Account not found"
        return "Customer not found" 

    def deposit(self, personalNumber, accountNumber, amount):
        for c in self.customers:
            if personalNumber == c.personalNumber:
                for a in c.accounts:
                    if a.accountNumber == accountNumber:
                        a.saldo +=amount
                        a.transactions.append(Transaction(amount = amount))
                        self.dataSource.refresh_database()
                        return True
                return False
        return False

    def withdraw(self, personalNumber, accountNumber, amount):
        for c in self.customers:
            if personalNumber == c.personalNumber:
                for a in c.accounts:
                    if a.accountNumber == accountNumber:
                        if a.saldo >= amount:
                            a.saldo -=amount
                            a.transactions.append(Transaction(amount = -amount))
                            self.dataSource.refresh_database()
                            return True
                        return False
                return False
        return False

    def close_account(self, personalNumber, accountNumber):
        for c in self.customers:
            if personalNumber == c.personalNumber:
                if len(c.accounts) == 1:
                    return (f"Account nr: {c.accounts[0].accountNumber} cannot be closed,"+
                        " customer must have at least one account")
                for a in c.accounts:
                    if a.accountNumber == accountNumber:
                        self.bankAccountFreeNumbers.append(a.accountNumber)
                        self.bankAccountFreeNumbers.sort()
                        moneyBack = a.saldo
                        number = accountNumber
                        c.accounts.remove(a)
                        self.dataSource.refresh_database()
                        return (f"Account: {number} for customer pn: {c.personalNumber}, name: {c.name} closed,"
                            f"withdrawn: {moneyBack}")
                return "Account not found"
        return "Customer not found"

    def get_all_transactions_by_pnr_acc_nr(self, personalNumber, accountNumber):
        a = self._get_account(personalNumber, accountNumber)
        if a is not None:
            return a.transactions
        return -1
