from collections import namedtuple
from peewee import CharField, DateTimeField, IntegerField, Check
from datetime import datetime
from .database import BaseModel, FallbackBaseModel

class Flag(BaseModel):
    value = CharField(unique=True)
    exploit = CharField()
    target = CharField()
    timestamp = DateTimeField(default=datetime.now)
    status = CharField(constraints=[Check("status IN ('queued', 'accepted', 'rejected')")])
    response = CharField(null=True)


class FallbackFlag(FallbackBaseModel):
    value = CharField()
    exploit = CharField()
    target = CharField()
    timestamp = DateTimeField(default=datetime.now)
    status = CharField(constraints=[Check("status IN ('pending', 'forwarded')")])
