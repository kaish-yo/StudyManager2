import sqlite3
from db import db
import datetime


class StudytimeModel(db.Model):
    __tablename__ = 'studytime'
    
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String)
    date = db.Column(db.Date)
    year = db.Column(db.String)
    month = db.Column(db.String)
    eachtime = db.Column(db.Integer)

    def __init__(self,userId, date, year, month, eachtime):
        self.userId = userId
        self.date = date
        self.year = year
        self.month = month
        self.eachtime = eachtime
    
    def save_to_database_total(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def sum_of_daily_total(cls, userId,date):
        recordlist = cls.query.filter_by(userId=userId).filter_by(date=date)
        total = 0
        for i in recordlist:
            total += i.eachtime
        return total
    
    @classmethod
    def sum_of_monthly_total(cls, userId, month):    
        recordlist = cls.query.filter_by(userId=userId).filter_by(year=str(datetime.date.today().year)).filter_by(month=month)
        total = 0
        for i in recordlist:
            total += i.eachtime
        return total
    
    @classmethod
    def sum_of_entire(cls, userId):
        recordlist = cls.query.filter_by(userId=userId)
        total = 0
        for i in recordlist:
            total += i.eachtime
        return total