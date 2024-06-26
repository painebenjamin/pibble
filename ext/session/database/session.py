#!/usr/bin/env python3
import datetime
from sqlalchemy import Column, String, DateTime
from fruition.database.orm import ORMEncryptedVariadicType
from fruition.ext.session.database.base import SessionExtensionObjectBase


class Session(SessionExtensionObjectBase):
    __tablename__ = "fruition_session"

    token = Column(String(32), primary_key=True)
    created = Column(DateTime, default=datetime.datetime.now())


class SessionDatum(SessionExtensionObjectBase):
    __tablename__ = "fruition_session_datum"

    session_token = Column(
        Session.ForeignKey("token", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    key = Column(String(128), primary_key=True)
    value = Column(ORMEncryptedVariadicType)


__all__ = ["Session", "SessionDatum"]
