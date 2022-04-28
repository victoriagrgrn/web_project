import datetime
import sqlalchemy
from sqlalchemy import orm
from . import users


from .db_session import SqlAlchemyBase


class News(SqlAlchemyBase):
    __tablename__ = 'foto'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    file = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    publisher = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    duration = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    publish_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)
    modified_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now)

    def __repr__(self):
        return f'<News> {self.id} {self.author} {self.name}'