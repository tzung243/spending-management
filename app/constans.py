import typing
import dataclasses


class WalletType:
    CASH = 1
    BANK = 2


class TransactionType:
    INCOME = 1
    EXPENSE = 2


@dataclasses.dataclass
class TransactionLabel:
    DINING: int = 1
    TRANSPORTATION: int = 2
    SHOPPING: int = 3
    BILLS: int = 4
    RENT: int = 5
    SALARY: int = 6
    TRANSFER: int = 7

class StaticsType:
    DAYS = 1
    MONTH = 2
