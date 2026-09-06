from http.client import HTTPException
from fastapi import FastAPI
from database import session, Product

app = FastAPI()

@app.get("/")
def hola_mundo():
    return "Hola mundo"


@app.get("/products")
def get_products():
    products = session.query(Product).all()
    return [vars(product) for product in products]

@app.get("/product/{productId}")
def get_product(productId: int):
    product = session.query(Product).get(productId)
    if product is None:
        raise HTTPException(status_code = 204, detail ="Producto no encontrado")
    return vars(product)


