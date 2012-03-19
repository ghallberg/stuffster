from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from werkzeug import generate_password_hash, check_password_hash

engine = create_engine('sqlite:///db_stuffster.db', echo=False)
Session = scoped_session(sessionmaker(bind=engine, autoflush=True))

Base = declarative_base()

#Database definition

association_table = Table('association', Base.metadata,
                          Column('cat_id', String,
                                 ForeignKey('categories.name')),
                          Column('link_id', Integer, ForeignKey('links.id')),
                         )


class User(Base):
    __tablename__= 'users'
    name = Column(String, primary_key=True)
    email_address = Column(String, unique=True)
    pw_hash = Column(String)
    note = Column(String, default = "")

    def __init__(self, name, email_address, password):
        self.name = name
        self.email_address = email_address
        self.set_password(password)

    def __rep__(self):
        return "<User('%s', '%s', '%s')>" % (self.name,
                                             self.email_address,
                                             self.pw_hash)

    def __str__(self):
        return self.__rep__()

    def check_password(self, given_pass):
        return check_password_hash(self.pw_hash, given_pass)

    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

class Category(Base):
    __tablename__ = 'categories'
    name = Column(String, nullable=False, primary_key=True)
    owner_id = Column(Integer, ForeignKey('users.name'), primary_key=True)
    owner = relationship("User", backref=backref('categories'), order_by=name)

    links=relationship("Link",
                       secondary=association_table,
                       backref="belongs_to",
                      )

    def __init__(self, owner, name):
        self.owner = owner
        self.name = name

    def __repr__(self):
        return "<Category('%s')>" % (self.name)

class Link(Base):
    def __init__(self, categories, address, name):
        self.belongs_to.extend(categories)
        self.address = address
        self.name = name
        num_clicks = 0
    __tablename__ = 'links'
    id = Column(Integer, primary_key=True)
    address = Column(String, nullable=False)
    name = Column(String, nullable=False)
    num_clicks = Column(Integer, nullable=False, default=0)

    def __repr__(self):
        return "<Link('%s', '%s')>" % (self.name, self.address)

Base.metadata.create_all(engine)

#Functions to access database

def add_user(name, address, password):
    session = Session()
    try:
        user = User(name, address, password)
        session.add(user)
        session.commit()
        
    except IntegrityError:
        print("Failed to add user")
    session.close()

def auth_user(username, password):
    session = Session()
    user = session.query(User).filter(User.name == username).first()
    print(user)

    if user:
        return user.check_password(password)

    return False

def add_link(catnames, name, address, username):
    """Adds a link to caegories in tuple catnames for user username"""
    session = Session()
    user = session.query(User).filter(User.name == username)[0]
    cats = []
    for catname in catnames:
        result = session.query(Category).\
                 filter(Category.owner_id == user.name).\
                 filter(Category.name == catname)

        if result.count() != 0:
            cat = result[0]

        else:
            cat = Category(user,catname)
        
        cats.append(cat)
        session.add(cat)
            
    session.add(Link(cats, address, name))
    session.commit()

def del_link(linkid, target_cat):
    """Removes the link with the given id"""
    session = Session()
    link = session.query(Link).\
            filter(Link.id == linkid).\
            first()

    if not link:
        return False

    #Delete link
    cats = session.query(Category).filter(Category.links.contains(link))
    for cat in cats:
        print cat.links
        print link
        if cat.name == target_cat:
            cat.links.remove(link)
            if len(cat.links) == 0:
                session.delete(cat)
    session.flush()
    session.commit()


    
    return True

def get_categories(username):
    session = Session()
    user = session.query(User).filter(User.name == username)[0]
    return user.categories

def save_note(new_note, user):
    session = Session()
    user = session.query(User).filter(User.name == user).first()
    if user:
        user.note = new_note
        return True

    return False

def get_note(user):
    session = Session()
    user = session.query(User).filter(User.name == user).first()
    if user:
        return user.note
    return ""
