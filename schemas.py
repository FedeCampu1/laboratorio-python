from datetime import date,time
from pydantic import BaseModel


class ProductCreate(BaseModel):
    name:str
    price:int

    class Config:
        from_attributes = True

class SaleCreate(BaseModel):
    date: date
    time: time
    quantity: int
    productId:int

    class Config:
        from_attributes = True