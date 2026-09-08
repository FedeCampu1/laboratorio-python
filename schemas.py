from datetime import date

from pydantic import BaseModel


class ProductCreate(BaseModel):
    name:str
    price:float

class SaleCreate(BaseModel):
    date: date
    cantidad: int
