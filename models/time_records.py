import sqlite3
from db import db

class TimeModel(db.Model):
    __tablename__ = 'items'

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.String)
    date = db.Column(db.Date)
    recordedtime = db.Column(db.Integer)
    start_end_flag = db.Column(db.Integer)

    #classの定義をする
    def __init__(self, userId, date, recordedtime, start_end_flag):
        # self.id = id
        self.userId = userId
        self.date = date
        self.recordedtime = recordedtime
        self.start_end_flag = start_end_flag

    #データベースに保存する用
    def save_to_database(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_last_data(cls, userId):
        return cls.query.filter_by(userId=userId).order_by(cls.id.desc()).first()

    
