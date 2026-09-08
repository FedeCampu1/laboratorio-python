from fastapi import FastAPI, HTTPException, status
from database import session, Product
from schemas import ProductCreate
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

@app.post("/product", status_code=status.HTTP_201_CREATED)
def add_product(data_product: ProductCreate):
    new_product = Product(
        name = data_product.name,
        price = data_product.price
    )
    session.add(new_product)
    try:
        session.commit()
        session.refresh(new_product)
    except:
        session.rollback()
        raise HTTPException(status_code=400, detail="Error al crear producto (nombre duplicado o datos invalidos)")
    return vars(new_product)

@app.put("/product/{productId}")
def update_product(productId, data_product: ProductCreate):
    product  = session.query(Product).get(productId)
    if product is None:
        raise HTTPException(status_code=204, detail="Producto no encontrado")
        product.name = data_product.name if data_product.name is not None else product.name
        product.price = data_product.price if data_product.price is not None else product.price

        session.commit()
        return vars(product)

@app.delete("/product/{productId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(productId):
    product = session.query(Product).get(productId)
    if product is None:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    session.delete(product)
    session.commit()
