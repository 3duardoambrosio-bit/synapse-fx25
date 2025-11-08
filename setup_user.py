from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt
from app import Base, User

engine = create_engine('sqlite:///synapse.db')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

password_hash = bcrypt.hashpw(b'test1234', bcrypt.gensalt()).decode()
user = User(email='test@test.com', password_hash=password_hash)
session.add(user)
session.commit()

print('✅ Usuario creado: test@test.com / test1234')
session.close()
