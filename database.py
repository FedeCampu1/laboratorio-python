from sqlalchemy import Date, ForeignKey,Time , create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker,  relationship

#Se crea la conexion con la db
engine = create_engine('sqlite:///my_database.db', echo=True)

# Se declara la base
Base = declarative_base()

#Tabla de productos
class Product(Base):
    __tablename__ = 'products'
    productId = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)


#Tabla de ventas
class Sale(Base):
    __tablename__ = 'sales'
    saleId = Column(Integer, autoincrement = True, nullable = False, primary_key = True)
    date = Column(Date, nullable = False)
    time = Column(Time, nullable = False)
    total_price = Column(Float, nullable=False)
    cartId = Column(Integer, ForeignKey('carts.cartId'), nullable=False, unique=True)
    
    cart = relationship("Cart")

class Cart(Base):
    __tablename__="carts"
    cartId = Column(Integer, autoincrement=True, nullable=False, primary_key=True)
    creation_date = Column(Date, nullable=False)
    status = Column(String, nullable=False)

    productsCart = relationship("ProductCart", back_populates="cart")

class ProductCart(Base):
    __tablename__="productsCart"
    productCartId = Column(Integer, autoincrement=True, nullable=False, primary_key= True)
    cartId = Column(Integer, ForeignKey("carts.cartId"), nullable=False)
    productId = Column(Integer, ForeignKey("products.productId"),nullable=False)
    quantity = Column(Integer, nullable=False)
    cart = relationship("Cart",  back_populates="productsCart")
    product = relationship("Product") 

#Se crean las tablas si no existen en el .db
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

#nuevo_producto = Product(name="Bebida", price = 1000)
#Session.add(nuevo_producto)
#Session.commit()