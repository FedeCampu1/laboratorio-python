from datetime import date,time
from pydantic import BaseModel

#PRODUCTO
class ProductCreate(BaseModel):
    name:str
    price:float

    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    productId:int
    name:str
    price:float


#VENTA
class SaleCreate(BaseModel):
    date: date
    time: time
    cartId:int
    class Config:
        from_attributes = True

class SaleResponse(BaseModel):
    saleId: int
    date: date
    time: time
    cart: CartResponse
    total_price: float

    class Config:
        from_attributes = True

class SaleCartAssign(BaseModel):
    cartId:int

#CARRITO DE PRODUCTO
class ProductCartResponse(BaseModel):
    productCartId:int
    product: ProductResponse
    quantity : int

    class Config:
        from_attributes = True

class ProductCartCreate(BaseModel):
    productId: int
    quantity : int

#CARRITO
class CartCreate(BaseModel):
    creation_date: date
    status: str

class CartResponse(BaseModel):
    cartId: int
    creation_date: date
    status: str
    productsCart:list[ProductCartResponse]

    class Config:
        from_attributes = True



