from sqlalchemy import Column, ForeignKey, Integer, String, DateTime

from app.database import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    email = Column(String(50), unique=True, nullable=False)


class Wallets(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type = Column(Integer, nullable=False)
    amount = Column(Integer, nullable=False)


class TransactionLabels(Base):
    __tablename__ = "transaction_labels"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    label_name = Column(String(50), nullable=False)


class Transactions(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    wallet_id = Column(
        Integer, ForeignKey("wallets.id", ondelete="CASCADE"), nullable=False
    )
    type = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False)
    description = Column(String(50))
    date = Column(DateTime, nullable=False)
    label = Column(
        Integer,
        ForeignKey("transaction_labels.id", ondelete="CASCADE"),
        nullable=True,
    )


class ActivityLogs(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    log = Column(String(50), nullable=False)
    transaction_id = Column(
        Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False
    )
