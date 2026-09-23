from fastapi import FastAPI, HTTPException, status
from database import session, Product, Sale
from schemas import ProductCreate, SaleCreate, SaleResponse
app = FastAPI()


@app.get("/")
def hola_mundo():
    return "Hola mundo"

# ABM Product

@app.get("/products", status_code=status.HTTP_200_OK)
def get_products():
    try:
        products = session.query(Product).all()
        response = {"products": products}
        return response
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get products: {e}")

@app.get("/products/{product_id}", status_code=status.HTTP_200_OK)
def get_product(product_id: int):
    try:
        product = session.query(Product).get(product_id)

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        response = {"product": product}
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get product with id {product_id}: {e}")


@app.post("/products", status_code=status.HTTP_201_CREATED)
def create_product(product_data: ProductCreate):
    try:
        product = session.query(Product).filter_by(name=product_data.name).first()

        if product:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product already exists")

        product = Product(
            name=product_data.name,
            price=product_data.price
        )

        session.add(product)
        session.commit()
        session.refresh(product)

        response = {"product": product}
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to create product: {e}")


@app.put("/products/{product_id}", status_code=status.HTTP_200_OK)
def update_product(product_id: int, product_data: ProductCreate):
    try:
        product = session.query(Product).get(product_id)

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        product.name = product_data.name
        product.price = product_data.price

        session.commit()
        session.refresh(product)

        response = {"product": product}
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to update product with id {product_id}: {e}")


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int):
    try:
        product = session.query(Product).get(product_id)

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        session.delete(product)
        session.commit()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to delete product with id {product_id}: {e}")


# ABM Sales

@app.get("/sales", status_code=status.HTTP_200_OK, response_model=list[SaleResponse])
def get_sales():
    try:
        sales = session.query(Sale).all()
        return sales
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get sales: {e}")


@app.get("/sales/{sale_id}", status_code=status.HTTP_200_OK, response_model=SaleResponse)
def get_sale(sale_id: int):
    try:
        sale = session.query(Sale).get(sale_id)

        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

        return sale
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get sale with id {sale_id}: {e}")



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


@app.put("/sales/{sale_id}", status_code=status.HTTP_200_OK, response_model=SaleResponse)
def update_sale(sale_id: int, data_sale: SaleCreate):
    try:
        sale = session.query(Sale).get(sale_id)

        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

        product = session.query(Product).get(data_sale.productId)

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        sale.date = data_sale.date
        sale.time = data_sale.time
        sale.quantity = data_sale.quantity
        sale.productId = data_sale.productId
        sale.total_price = data_sale.quantity * product.price

        session.commit()
        session.refresh(sale)

        return sale
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to update sale with id {sale_id}: {e}")


@app.delete("/sales/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(sale_id: int):
    try:
        sale = session.query(Sale).get(sale_id)

        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

        session.delete(sale)
        session.commit()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to delete sale with id {sale_id}: {e}")