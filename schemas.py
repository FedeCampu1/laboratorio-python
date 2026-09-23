from datetime import date,time
from pydantic import BaseModel


class ProductCreate(BaseModel):
    name:str
    price:int

    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    productId:int
    name:str
    price:int



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
