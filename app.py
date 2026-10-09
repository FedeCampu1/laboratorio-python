from fastapi import FastAPI, HTTPException, status
from database import session, Product, Sale, Cart, ProductCart
from schemas import ProductCreate, SaleCreate, SaleResponse, CartCreate, CartResponse, ProductCartCreate, ProductCartResponse
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

        productCart = session.query(ProductCart).filter(ProductCart.productId == product_id).first()

        if productCart:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede eliminar un producto registrado en un carrito")

        session.delete(product)
        session.commit()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to delete product with id {product_id}: {e}")


# ========== ABM Sales ===========

@app.get("/sales", status_code=status.HTTP_200_OK, response_model=list[SaleResponse])
def get_sales():
    try:
        sales = session.query(Sale).all()
        return sales
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get sales: {e}")


@app.get("/sales/{sale_id}", status_code=status.HTTP_200_OK, response_model=SaleResponse)
def get_saleId(saleId: int):
    try:
        sale = session.query(Sale).get(saleId)

        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

        return sale
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get sale with id {saleId}: {e}")

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

#TODO: Me falta el POST para asignar una venta a un carrito


#============ ABM CARRITO =========

@app.get("/carts", status_code=status.HTTP_200_OK, response_model=list[CartResponse])
def get_carts():
    try: 
        cart = session.query(Cart).all()
        return cart
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el carrito: {e}")

@app.post("/carts", status_code=status.HTTP_201_CREATED)
def add_cart(cartCreate:CartCreate):
    try:
        cart = Cart(
            creation_date = cartCreate.creation_date,
            status =cartCreate.status
        )

        session.add(cart)
        session.commit()
        session.refresh(cart)

        response = {"cart": cart }
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocurrio un error al crear un carrito: {e}")

@app.post("/carts/{cartId}/products", status_code=status.HTTP_201_CREATED)
def add_productCart(productCartCreate: ProductCartCreate):
    try:
        productCart = ProductCart(
            cartId = productCartCreate.cartId,
            productId = productCartCreate.productId,
            amount = productCartCreate.amount
        )

        session.add(productCart)
        session.commit()
        session.refresh(productCart)
        response = {"ProductCart": productCart}
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocurrio un error al crear un carrito de productos: {e}")
   
#TODO: hacer en el get de carritos, traer tambien a la tabla de cart product,
# haciendo primero un get a productCart busncaod por cartId, las que encuentra las pone en get de cart

@app.get("/carts/{cartId}", status_code=status.HTTP_200_OK, response_model=CartResponse)
def get_cartId(cartId:int):
    try:
        cart = session.query(Cart).get(cartId)

        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")

        return cart
    except HTTPException:
      raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocurrio un error al obtener el carrito {cartId}: {e}")
    