import logging
import transaction
import datetime as date

from sqlalchemy import Table, Text, Column, Numeric, Integer, String, ForeignKey, Sequence, Unicode, select, func, desc, asc, distinct, not_

from sqlalchemy.types import DateTime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import scoped_session, sessionmaker, relation, backref
from sqlalchemy.ext.declarative import declarative_base

from zope.sqlalchemy import ZopeTransactionExtension
from paas.helpers import *

DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()

appDeploy = Table('APP_DEPLOY', Base.metadata,
                    Column('APP_ID', Integer, ForeignKey('APPLICATION.ID')),
                    Column('DEPLOY_ID', Integer, ForeignKey('DEPLOY.ID'))
            )
"""
    DROP TABLE APP_DEPLOY;
    CREATE TABLE APP_DEPLOY (
        APP_ID      NUMBER(38) NOT NULL,
        DEPLOY_ID   NUMBER(38) NOT NULL,
        CONSTRAINT PK_APP_DEPLOY PRIMARY KEY (APP_ID, DEPLOY_ID),
        CONSTRAINT FK_APP_ID FOREIGN KEY (APP_ID) REFERENCES APPLICATION (APP_ID),
        CONSTRAINT FK_DEPLOY_ID FOREIGN KEY (DEPLOY_ID) REFERENCES DEPLOY (DEPLOY_ID)
    );
    SELECT * FROM APP_DEPLOY;
"""

class Application(Base):
    """
    DROP TABLE APPLICATION;
    CREATE TABLE APPLICATION
    (
        ID              NUMBER(38) NOT NULL,
        NAME            VARCHAR2(50) NULL,
        EMAIL           VARCHAR2(2000) NULL,
        DESCRIPTION     VARCHAR2(4000) NULL,
        CONTAINER_TYPE  VARCHAR2(500) NULL,
        CREATED_DATE    DATE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        CONSTRAINT PK_APPLICATION PRIMARY KEY (ID)
    );
    """
    __tablename__   = 'APPLICATION'

    id              = Column('ID', Integer, primary_key=True)
    name            = Column('NAME', Unicode(50), nullable=True)
    email           = Column('EMAIL', Unicode(2000), nullable=True)
    description     = Column('DESCRIPTION', Unicode(4000), nullable=True)
    containerType   = Column('CONTAINER_TYPE', Unicode(500), nullable=True, default=0)
    createdDate     = Column('CREATED_DATE', DateTime, nullable=False)
    updatedDate     = Column('UPDATED_DATE', DateTime, nullable=True)
    deploys         = relation('Deploy', secondary=appDeploy, backref='applications', lazy=False)

    def getAll(self):
        results = DBSession().query(self.__class__).all()
        return results

    def getById(self, id=None):
        if not id: return
        result = DBSession().query(self.__class__).filter(self.__class__.id==id).one()
        return result

    def getSet(self, limit=10, offset=0):
        return DBSession().query(self.__class__).order_by(desc(self.__class__.createdDate), desc(self.__class__.id)).limit(limit).offset(offset).all()

    def getTotal(self):
        return DBSession().query(self.__class__).count()

    def setParams(self, params):
        for attr in params.keys():
            value = params.get(attr)
            if value: setattr(self, attr, value)
        self.updatedDate = date.datetime.today()
        if not self.createdDate:
            self.createdDate = date.datetime.today()

    def create(self, params):
        self.setParams(params)
        session = DBSession()
        session.add(self)
        return

    def update(self, params):
        self.setParams(params)
        session = DBSession()
        return

    def delete(self):
        session = DBSession()
        session.delete(self)
        return

class Deploy(Base):
    """
    DROP TABLE DEPLOY;
    CREATE TABLE DEPLOY (
        ID              NUMBER(38) NOT NULL,
        NAME            VARCHAR2(55) NOT NULL,
        VERSION         VARCHAR2(4000) NOT NULL,
        CREATED_DATE    DATE DEFAULT CURRENT_TIMESTAMP NOT NULL,
        UPDATED_DATE    DATE NULL,
        CONSTRAINT PK_DEPLOY PRIMARY KEY (ID)
    );
    SELECT * FROM DEPLOY;
    """

    __tablename__   = 'DEPLOY'

    id              = Column('ID', Integer, primary_key=True)
    name            = Column('NAME', Unicode(55))
    version         = Column('VERSION', Unicode(4000))
    createdDate     = Column('CREATED_DATE', DateTime, nullable=False)
    updatedDate     = Column('UPDATED_DATE', DateTime, nullable=True)

    def getAll(self):
        return DBSession().query(self.__class__).order_by(self.__class__.id).all()

    def getById(self, id=None):
        if not id: return
        return DBSession().query(self.__class__).filter_by(id=id).one()

    def setParams(self, params=None):
        if not params: return self
        self.name        = params.get('name')
        self.version     = params.get('version')
        self.updatedDate = date.datetime.today()
        if not self.createdDate:
            self.createdDate = date.datetime.today()

    def create(self, params):
        self.setParams(params)
        session = DBSession()
        session.add(self)
        return

    def update(self, params):
        self.setParams(params)
        session = DBSession()
        return

    def delete(self):
        session = DBSession()
        session.delete(self)
        return


## For Testing Framework ##
class MyModel(Base):
    __tablename__ = 'models'
    id    = Column(Integer, primary_key=True)
    name  = Column(Text, unique=True)
    value = Column(Integer)

    def __init__(self, name, value):
        self.name = name
        self.value = value

