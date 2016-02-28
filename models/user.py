import datetime
import uuid

from flask import session

from common.database import Database
from models.blog import Blog

__author__ = "MarcioDaSilva"


class User(object):
    def __init__(self, email, password, _id=None):
        self.email = email
        self.password = password
        self._id = uuid.uuid4().hex if _id is None else _id

    @classmethod
    def get_by_email(cls, email):
        data = Database.find_one("users", {"email": email})
        if data is not None:
            return cls(**data)

    @classmethod
    def get_by_id(cls, _id):
        data = Database.find_one("users", {"_id": _id})
        if data is not None:
            return cls(**data)
        return None

    @staticmethod
    def login_valid(email, password):
        # check whether or not the user name and password is valid
        user = User.get_by_email(email)
        if user is not None:
            return user.password == password
        return False

    @classmethod
    def register(cls, email, password):
        user = cls.get_by_email(email)
        if user is None:
            new_user = cls(email, password)
            new_user.save_to_mongo()
            session["email"] = new_user.email
            return True
        else:
            # User already exists
            # display message to the user
            return False

    @staticmethod
    def login(user_email):
        session["email"] = user_email

    @staticmethod
    def logout():
        session["email"] = None

    def get_blogs(self):
        return Blog.find_by_author_id(self._id)

    def new_blog(self):
        blog = Blog(author=self.email,
                    title=self.title,
                    description=self.description,
                    author_id=self._id)
        blog.save_to_mongo()

    @staticmethod
    def new_post(blog_id, title, content, date=datetime.datetime.utcnow()):
        blog = Blog(blog_id)
        blog.new_post(title=title, content=content, date=date)

    def json(self):
        return {
            "email": self.email,
            "_id": self._id,
            "password": self.password
        }

    def save_to_mongo(self):
        Database.insert("users", self.json())
