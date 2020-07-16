#!/usr/bin/env python3
from sqlalchemy import create_engine, Column, String, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


# Create User table.
class User(Base):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)


# Create Genre table.
class Genre(Base):

    __tablename__ = "genre"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Return data in serializable format.
    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id
        }


# Create Book table.
class Book(Base):

    __tablename__ = "book"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    genre = relationship(Genre)
    user = relationship(User)
    genre_id = Column(Integer, ForeignKey('genre.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    # Return data in serializable format.
    @property
    def serialize(self):

        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'user_id': self.user_id,
            'genre_id': self.genre_id,
        }


engine = create_engine('sqlite:///BookDatabase.db')
Base.metadata.create_all(engine)
