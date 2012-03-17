#:coding=utf-8:

from newauth.api import UserBase, AnonymousUserBase, BasicUserBase

class TestUser(UserBase):
    pass

class TestBasicUser(BasicUserBase):
    pass

class TestUser3(UserBase):
    pass

class TestAnonymousUser3(AnonymousUserBase):
    pass
