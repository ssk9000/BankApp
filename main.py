from bankmodules import Account, Customer, Transaction, Bank, BankTui, DataSource

    
if __name__ == "__main__":   
    tui = BankTui(bank = Bank(name = "I-Bank", dataSource = DataSource()))
    tui.runMenu()

    
