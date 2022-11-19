class Account:
    def __init__(self, saldo = 0, accountType = "debit", accountNumber = 0):
        self.saldo = saldo
        self.accountType = accountType
        self.accountNumber = accountNumber
        self.transactions = []
