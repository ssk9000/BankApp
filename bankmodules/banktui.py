import os
import sys
import time
from readchar import readkey, key

#terminal windows size
WIDTH = 110 #columns
HEIGHT = 45 #rows

#regional settings
VALUTA = "SEK"

def printXY(x, y, text, color):
       print(f"\033[{x};{y}H", end = "")#set cursor position
       print(f"\u001b[38;5;{color}m{text}")#color print    

class BankTui:
    def __init__(self, bank = None):
        if sys.platform == "win32":
            os.system(f"mode con cols={WIDTH} lines={HEIGHT}")
        elif sys.platform == "linux" or sys.platform == "darvin": # ??? darvin == macOS
            os.system(f"stty cols {WIDTH} rows {HEIGHT}")    
        self.bank = bank
        self.currentCustomerPersonalNumber = 0
        self.currentAccountNumber = 0
        print("\u001b[44m") #set background color blue                     
        self.register_main_menu_items()

        
    def register_main_menu_items(self):
       self.currentCustomerPersonalNumber = 0
       self.currentAccountNumber = 0
       self.cursorPosition = 0
       self.menuTitle = "Main menu"
       self.menuItems = {}
       #register menu items
       self.menuItems["Select a registered customer"] = self.SelectRegisteredCustomer
       self.menuItems["Add new customer"] = self.addNewCustomer
       self.menuItems["Exit"] = self.Exit
       #end register menu items

    def runMenu(self):
        while True:
            print("\u001b[2J") # clear screen
            print("\x1b[?25l") #hide cursor
            position = 0
            title = " control terminal"
            l = len(self.bank.name)+len(title)
            printXY(5, int((WIDTH - l) / 2), self.bank.name+title, 210)
            printXY(10, int((WIDTH - len(self.menuTitle)) / 2), self.menuTitle, 210)
            for item in self.menuItems:
                locate = int((WIDTH - len(item)) / 2) #center position
                if position == self.cursorPosition:
                    printXY(15 + 2*position, locate - 5, f"$$$  {item}  $$$", 222)
                else:        
                    printXY(15 + 2*position, locate, item, 218)
                position+=1            
            k = readkey() 
            if k == key.DOWN:
                if self.cursorPosition == (len(self.menuItems)- 1):
                    self.cursorPosition = 0
                else:
                    self.cursorPosition+=1                
            elif k == key.UP:
                if self.cursorPosition == 0:
                    self.cursorPosition = (len(self.menuItems)- 1)
                else:
                    self.cursorPosition-=1   
            elif k == key.ENTER:
                self.menuItems[list(self.menuItems.keys())[self.cursorPosition]]()
                
            time.sleep(0.2)

    def setupMenu(self, title):
        self.cursorPosition = 0
        self.menuTitle = title
        self.menuItems["Back to main menu"] = self.mainMenu

    def SelectRegisteredCustomer(self):
        customersInfo = self.bank.get_customers()
        self.menuItems = {}
        for c in customersInfo:
               self.menuItems[f"Personal number: {c[0]} | Name: {c[1]} | ID: {c[2]}"] = self.customerMenu
        self.setupMenu("Choose a registered customer")
        return

    def mainMenu(self):
        self.register_main_menu_items()
        self.runMenu()
           
    def customerMenu(self):
        customerTextLine = list(self.menuItems.keys())[self.cursorPosition]   #get key value from dictionary by position number
        self.currentCustomerPersonalNumber = int(customerTextLine.split(" ")[2]) #parse customer person number which between second and third spaces        
        self.menuItems = {}
        self.menuItems["Change name"] = self.changeName
        self.menuItems["Add new account"] = self.addAccount
        accountsInfo = self.bank.get_customer(self.currentCustomerPersonalNumber)
        for a in accountsInfo:
              self.menuItems[f"Account number: {a[0]} | type: {a[1]} | Saldo: {a[2]} {VALUTA}"] = self.accountMenu
        self.menuItems["Remove customer"] = self.removeCustomer
        self.setupMenu(f"Choose some option for customer pn: {self.currentCustomerPersonalNumber} or choose one account to do operations. ")
        return

    def accountMenu(self):
        accountTextLine = list(self.menuItems.keys())[self.cursorPosition]
        self.currentAccountNumber = int(accountTextLine.split(" ")[2])
        self.menuItems = {}
        self.menuItems["Deposit"] = self.deposit
        self.menuItems["Withdraw"] = self.withdraw
        self.menuItems["Show transactions under current session"] = self.showTransactions #transactions are not saved in the database can view only for current session
        self.menuItems["Close account"] = self.closeAccount
        self.setupMenu(f"Choose operations for account: {self.currentAccountNumber} belongs customer with personal number: {self.currentCustomerPersonalNumber}")
        return

    def deposit(self):
        print("\u001b[2J") #clear screen
        title = f"How much you want to deposit:"
        printXY(15, int((WIDTH - len(title)) / 2), title, 180)
        print("\x1b[?25h") #show cursor
        print(f"\033[{17};{int(WIDTH / 2)}H", end = "")#set cursor position
        amount = float(input()) #TODO: check if input is float type
        self.bank.deposit(self.currentCustomerPersonalNumber, self.currentAccountNumber, amount)
        self.menuItems = {}
        self.setupMenu(f"{amount} {VALUTA} deposited to account number: {self.currentAccountNumber}")
        return

    def withdraw(self):
        print("\u001b[2J") #clear screen
        title = f"How much you want to withdraw:"
        printXY(15, int((WIDTH - len(title)) / 2), title, 180)
        print("\x1b[?25h") #show cursor
        print(f"\033[{17};{int(WIDTH / 2)}H", end = "")#set cursor position
        amount = float(input()) #TODO: check if input is float type
        result = self.bank.withdraw(self.currentCustomerPersonalNumber, self.currentAccountNumber, amount)
        if result:
               title = f"{amount} {VALUTA} withdrawn from account number: {self.currentAccountNumber}"
        else:
               title = f"Not enough money on account number: {self.currentAccountNumber}"
        self.menuItems = {}
        self.setupMenu(title)
        return

    def showTransactions(self):
        trans = self.bank.get_all_transactions_by_pnr_acc_nr(self.currentCustomerPersonalNumber,self.currentAccountNumber)
        self.menuItems = {}
        if trans == []:
            title = f"There are no transactions under the current session for account: {self.currentAccountNumber}"
        else:
            title = (f"Transactions for account: {self.currentAccountNumber}"
                f" belongs customer with personal number: {self.currentCustomerPersonalNumber}")
            for t in trans:
                if t.amount >0:
                    x = "Deposit"
                else:
                    x = "Withdrawn"
                self.menuItems[f"{x} amount: {abs(t.amount)}, date-time: {t.dt}"] = self.dummy     
        self.setupMenu(title)
        return

    def dummy(self):
        pass
        
    def closeAccount(self):
        self.menuItems = {}
        self.setupMenu(self.bank.close_account(self.currentCustomerPersonalNumber,
               self.currentAccountNumber))
        return     
       
    def addAccount(self):
        newAccountNumber = self.bank.add_account(self.currentCustomerPersonalNumber)
        self.menuItems = {}
        self.setupMenu(f"New account number: {newAccountNumber} for customer pn: {self.currentCustomerPersonalNumber} created")
        return
           
    def changeName(self):
        print("\u001b[2J") #clear screen
        title = f"Input new name for customer with personal numner {self.currentCustomerPersonalNumber}"
        printXY(15, int((WIDTH - len(title)) / 2), title, 180)
        print("\x1b[?25h") #show cursor
        print(f"\033[{17};{int(WIDTH / 2)}H", end = "")#set cursor position
        newName = input()
        self.bank.change_customer_name(self.currentCustomerPersonalNumber, newName)
        self.menuItems = {}
        self.setupMenu(f"Name for customer pn: {self.currentCustomerPersonalNumber} was changed to {newName}")
        return

    def removeCustomer(self):
        closeReport = self.bank.remove_customer(self.currentCustomerPersonalNumber)
        self.menuItems = {}
        self.setupMenu(f"Customer pn: {closeReport[0][0]} deleted, got money back from closed account(s): {closeReport[-1]} {VALUTA}")
        return

    def addNewCustomer(self):
        print("\u001b[2J") #clear screen
        title = f"Please input personal number for new customer:"
        printXY(15, int((WIDTH - len(title)) / 2), title, 180)
        print("\x1b[?25h") #show cursor
        print(f"\033[{17};{int(WIDTH / 2)-4}H", end = "") #set cursor position
        personalNumber = int(input())  #TODO: check if its integer
        title = f"New customers name:"
        printXY(19, int((WIDTH - len(title)) / 2), title, 180)
        print(f"\033[{21};{int(WIDTH / 2)-5}H", end = "") #set cursor position
        name = input()
        self.bank.add_customer(name, personalNumber)
        self.menuItems = {}
        self.setupMenu(f"New customer created with name: {name}, personal number: {personalNumber}")
        return

    def Exit(self):
        print("\u001b[40m")
        print("\x1b[?25h")
        print("\u001b[0m")
        print("\u001b[2J") # clear screen
        exit()     

