
from datetime import datetime

class Transaction:
    def __init__(self, dt  = str(datetime.now()).split(".")[0], amount = 0):
        self.dt = dt
        self.amount = amount
