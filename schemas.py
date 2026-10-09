from datetime import date,time
from pydantic import BaseModel

#PRODUCTO
class ProductCreate(BaseModel):
    name:str
    price:int

    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    productId:int
    name:str
    price:int


#VENTA
class SaleCreate(BaseModel):
    date: date
    time: time
    quantity: int
    productId:int

    class Config:
        from_attributes = True

class SaleResponse(BaseModel):
    saleId:int
    date: date
    time: time
    quantity: int
    productId:int
    total_price:float

#CARRITO DE PRODUCTO
class ProductCartResponse(BaseModel):
    productCartId:int
    product: ProductResponse
    amount : int

    class Config:
        from_attributes = True

class ProductCartCreate(BaseModel):
    cartId: int
    productId: int
    amount : int

#CARRITO
class CartCreate(BaseModel):
    creation_date: date
    status: str

class CartResponse(BaseModel):
    cartId: int
    creation_date: date
    status: str
    products:list[ProductCartResponse]

    class Config:
        from_attributes = True



