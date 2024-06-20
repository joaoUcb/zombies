class Wallet:
    def __init__(self):
        self.coins = 0

    def add_coins(self, amount):
        self.coins += amount

    def get_coins(self):
        return self.coins
