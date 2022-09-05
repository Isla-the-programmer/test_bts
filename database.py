import sqlite3
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, Column, Integer, Text, VARCHAR, Float, insert
from sqlalchemy.orm import Session

Base = declarative_base()


class table_debtor(Base):
    __tablename__ = "table_debtor"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    iin = Column(Text)
    debtor_name = Column(Text)
    debtor_address = Column(Text)
    bancruptcy_date = Column(Text)
    manager_date = Column(Text)
    manager_name = Column(Text)
    manager_term_start = Column(Text)
    manager_term_end = Column(Text)
    requirements_address = Column(Text)
    contacts = Column(Text)
    ad_date = Column(Text)



class Database:
    def __init__(self,):
        self.connection_obj = sqlite3.connect('test')
        self.cursor_obj = self.connection_obj.cursor()
        self.engine = create_engine('sqlite:///test')

    def create_table(self):
        table = """ CREATE TABLE IF NOT EXISTS table_debtor (
            ID int PRIMARY KEY NOT NULL,
            iin text,
            debtor_name text,
            Last_Name text,
            debtor_number text,
            debtor_address text,
            bancruptcy_date text,
            manager_date text,
            manager_name text,
            manager_term_start text,
            manager_term_end text,
            requirements_address text,
            contacts text,
            ad_date text
            ); """
        self.cursor_obj.execute(table)

    def close_connection(self):
        self.connection_obj.close()

    def insert_data(self, df):
        with Session(self.engine) as session:
            for k,row in df.iterrows():
                exists = session.query(table_debtor.id).filter_by(iin=row['iin']).first() is not None
                last_id = session.query(table_debtor).order_by(table_debtor.id.desc()).first()
                if not exists:
                    table = table_debtor(
                        id = last_id.id + 1 if last_id is not None else 1,
                        iin=row['iin'],
                        debtor_name = row['debtor_name'],
                        debtor_address = row['debtor_address'],
                        bancruptcy_date = str(row['bancruptcy_date']),
                        manager_date = str(row['manager_date']),
                        manager_name = row['manager_name'],
                        manager_term_start = str(row['manager_term_start']),
                        manager_term_end = str(row['manager_term_end']),
                        requirements_address = row['requirements_address'],
                        contacts = row['contacts'],
                        ad_date = str(row['ad_date'])
                    )
                    session.add(table)
                    session.commit()
