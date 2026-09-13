from fastapi import FastAPI, HTTPException, status
from database import session, Product, Sale
from schemas import ProductCreate, SaleCreate
app = FastAPI()


@app.get("/")
def hola_mundo():
    return "Hola mundo"

# ABM Product

@app.get("/products")
def get_products():
    products = session.query(Product).all()
    return [vars(product) for product in products]


@app.get("/product/{productId}")
def get_productId(productId: int):
    product = session.query(Product).get(productId)
    if product is None:
        raise HTTPException(status_code=204, detail="Producto no encontrado")
    return vars(product)


@app.post("/product", status_code=status.HTTP_201_CREATED)
def add_product(data_product: ProductCreate):
    new_product = Product(
        name=data_product.name,
        price=data_product.price
    )
    session.add(new_product)
    try:
        session.commit()
        session.refresh(new_product)
    except:
        session.rollback()
        raise HTTPException(
            status_code=400, detail="Error al crear producto (nombre duplicado o datos invalidos)")
    return vars(new_product)


@app.put("/product/{productId}")
def update_product(productId, data_product: ProductCreate):
    product = session.query(Product).get(productId)
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
        raise HTTPException(status_code=204, detail="Producto no encontrado")
    session.delete(product)
    session.commit()


# ABM Sales

@app.get("/sales")
def get_sales():
    sales = session.query(Sale).all()
    return [vars(sale) for sale in sales]


@app.get("/sales/{saleId}")
def get_saleId(saleId: int):
    sale = session.query(Sale).get(saleId)
    if sale is None:
        raise HTTPException(status_code=204, detail="Venta no encontrada")
    return vars(sale)


@app.post("/sale", status_code=status.HTTP_201_CREATED)
def add_sale(data_sale: SaleCreate):
    try:
        product = session.query(Product).get(data_sale.productId)

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

        sale = Sale(
            date=data_sale.date,
            time=data_sale.time,
            quantity=data_sale.quantity,
            productId=data_sale.productId,
            total_price=(data_sale.quantity * product.price)
        )

        session.add(sale)
        session.commit()
        session.refresh(sale)

        return sale
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocurrio un error al crear la venta: {e}")


@app.put("/sale/{saleId}")
def update_sale(data_sale: SaleCreate, saleId):
    sale = session.query(Sale).get(saleId)

    if sale is None:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="Venta no encontrado")
    sale.date = data_sale.date if data_sale.date is not None else sale.date
    sale.time = data_sale.time if data_sale.time is not None else sale.time
    sale.quantity = data_sale.quantity if data_sale.quantity is not None else sale.quantity
    sale.productId = data_sale.productId if data_sale.productId is not None else sale.productId

    product = session.query(Product).get(sale.productId)
    sale.total_price = sale.quantity * product.price

    session.commit()
    return vars(sale)



@app.delete("/sale/{saleId}",status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(saleId):
    sale = session.query(Sale).get(saleId)
    if sale is None:
        raise HTTPException(status_code=204, detail="No se encontro la venta")
    session.delete(sale)
    session.commit()