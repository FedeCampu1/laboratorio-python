from fastapi import FastAPI, HTTPException, status
from database import session, Product, Sale, Cart, ProductCart
from schemas import ProductCreate, SaleCreate, SaleResponse, CartCreate, CartResponse, ProductCartCreate, ProductCartResponse,ProductResponse,SaleCartAssign
app = FastAPI()


# ABM Product

@app.get("/products", status_code=status.HTTP_200_OK,response_model=list[ProductResponse])
def get_products():
    try:
        products = session.query(Product).all()
        return products
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get products: {e}")

@app.get("/products/{productId}", status_code=status.HTTP_200_OK, response_model=ProductResponse)
def get_product(productId: int):
    try:
        product = session.query(Product).get(productId)

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get product with id {productId}: {e}")


@app.post("/products", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
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

        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to create product: {e}")


@app.put("/products/{productId}", status_code=status.HTTP_200_OK, response_model=ProductResponse)
def update_product(productId: int, product_data: ProductCreate):
    try:
        product = session.query(Product).get(productId)

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        product.name = product_data.name
        product.price = product_data.price

        session.commit()
        session.refresh(product)

        return product
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to update product with id {productId}: {e}")

#eliminar producto si no esta asociado en un carrito
@app.delete("/products/{productId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(productId: int):
    try:
        product = session.query(Product).get(productId)

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        productCart = session.query(ProductCart).filter(ProductCart.productId == productId).first()

        if productCart:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede eliminar un producto registrado en un carrito")

        session.delete(product)
        session.commit()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to delete product with id {productId}: {e}")


# ========== ABM Sales ===========

def calculate_cart_total(cart):
    total = 0
    for item in cart.productsCart:
        subtotal = item.product.price * item.quantity
        total = total + subtotal
    return total

@app.get("/sales", status_code=status.HTTP_200_OK, response_model=list[SaleResponse])
def get_sales():
    try:
        sales = session.query(Sale).all()
        return sales
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to get sales: {e}")

@app.get("/sales/{saleId}", status_code=status.HTTP_200_OK, response_model=SaleResponse)
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

#creo una venta
@app.post("/sales", status_code=status.HTTP_201_CREATED, response_model=SaleResponse)
def add_sale(data_sale: SaleCreate):
    try:
        cart = session.query(Cart).get(data_sale.cartId)

        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")

        if cart.status != "cerrado":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El carrito debe estar cerrado")

        sale_cart = session.query(Sale).filter(Sale.cartId == data_sale.cartId).first()

        if sale_cart:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El carrito ya se encuentra en otra venta")

        sale = Sale(
            date=data_sale.date,
            time=data_sale.time,
            cartId=cart.cartId,
            total_price=calculate_cart_total(cart)
        )

        session.add(sale)
        session.commit()
        session.refresh(sale)

        return sale
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocurrio un error al crear la venta: {e}")
    
#asigno un carrito a una venta
@app.post("/sales/{saleId}/cart", status_code=status.HTTP_200_OK, response_model=SaleResponse)
def assign_cart_to_sale(saleId:int, data:SaleCartAssign):
    try:
        sale = session.query(Sale).get(saleId)

        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Venta no encontrada")

        cart = session.query(Cart).get(data.cartId)

        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrada")  

        if cart.status != "cerrado":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Carrito abierto")  

        sale_cart = session.query(Sale).filter(Sale.cartId == data.cartId, Sale.saleId != saleId).first()

        if sale_cart:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Carrito ya se encuentra en otra venta")  

        sale.cartId = cart.cartId
        sale.total_price = calculate_cart_total(cart)

        session.commit()
        session.refresh(sale)

        return sale
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocurrio un error al insertar un carrito en una venta: {e}")

#actualizar una venta y verificar que el carrito no este en otra venta
@app.put("/sales/{saleId}", status_code=status.HTTP_200_OK, response_model=SaleResponse)
def update_sale(saleId: int, data_sale: SaleCreate):
    try:
        sale = session.query(Sale).get(saleId)

        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

        cart = session.query(Cart).get(data_sale.cartId)

        if not cart: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")

        if cart.status != "cerrado":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El carrito debe estar cerrado")
        
        sale_cart = session.query(Sale).filter(Sale.cartId == data_sale.cartId,Sale.saleId != saleId).first()

        if sale_cart:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El carrito ya esta en otra venta")

        sale.date = data_sale.date
        sale.time = data_sale.time
        sale.cartId = data_sale.cartId
        sale.total_price = calculate_cart_total(cart)

        session.commit()
        session.refresh(sale)

        return sale
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to update sale with id {saleId}: {e}")

#elimino una venta
@app.delete("/sales/{saleId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(saleId: int):
    try:
        sale = session.query(Sale).get(saleId)

        if not sale:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sale not found")

        session.delete(sale)
        session.commit()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while trying to delete sale with id {saleId}: {e}")
    

#============ ABM CARRITO =========

#obtener carrito
@app.get("/carts", status_code=status.HTTP_200_OK, response_model=list[CartResponse])
def get_carts():
    try: 
        cart = session.query(Cart).all()
        return cart
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al obtener el carrito: {e}")

#crear un carrito
@app.post("/carts", status_code=status.HTTP_201_CREATED, response_model=CartResponse)
def add_cart(cartCreate:CartCreate):
    try:
        cart = Cart(
            creation_date = cartCreate.creation_date,
            status = cartCreate.status
        )

        session.add(cart)
        session.commit()
        session.refresh(cart)

        return cart
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocurrio un error al crear un carrito: {e}")

#asignar producto en un carrito
@app.post("/carts/{cartId}/products", status_code=status.HTTP_201_CREATED, response_model=CartResponse)
def add_productCart(cartId: int, productCartCreate: ProductCartCreate):
    try:

        cart = session.query(Cart).get(cartId)

        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found")

        if cart.status != "abierto":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede crear un producto de un carrito cerrado")

        product = session.query(Product).get(productCartCreate.productId)

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto not found")

        if productCartCreate.quantity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La cantidad debe ser mayor a 0")
        
        productCart = session.query(ProductCart).filter(ProductCart.cartId == cartId, ProductCart.productId == productCartCreate.productId).first()

        if not productCart:

            productCart = ProductCart(
            cartId = cartId,
            productId = productCartCreate.productId,
            quantity = productCartCreate.quantity
        )
            session.add(productCart)
        else:
            productCart.quantity += productCartCreate.quantity

        session.commit()
        session.refresh(cart)
        return cart
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ocurrio un error al crear un carrito de productos: {e}")
   
#get de carrito
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

#actualizar carrito que no este en una venta
@app.put("/carts/{cartId}",status_code=status.HTTP_200_OK, response_model=CartResponse)
def update_cart(cartId:int, cart_data:CartCreate):
    try:
        cart = session.query(Cart).get(cartId)

        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")

        sale_cart = session.query(Sale).filter(Sale.cartId == cartId).first()

        if sale_cart:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El carrito se encuentra en una venta y no puede modificarse")
        
        cart.creation_date = cart_data.creation_date
        cart.status = cart_data.status

        session.commit()
        session.refresh(cart)

        return cart
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al intentar actualiar el carrito {cartId}: {e}")

#eliminar carrito y sus productos. No debe estar en una venta
@app.delete("/carts/{cartId}",status_code=status.HTTP_204_NO_CONTENT)
def delete_cart(cartId:int):
    try:

        cart = session.query(Cart).get(cartId)

        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")

        sale_cart = session.query(Sale).filter(Sale.cartId == cartId).first()

        if sale_cart:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El carrito se encuentra en una venta y no puiede eliminarse")


        session.query(ProductCart).filter(cart.cartId == ProductCart.cartId).delete()

        session.delete(cart)
        session.commit()

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"No se puede eliminar el carrito {cartId}: {e}")

#eliminar producto de un carrito
@app.delete("/carts/{cartId}/products/{productId}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cartId_productId(cartId: int, productId: int):
    try:
        cart = session.query(Cart).get(cartId)

        if not cart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Carrito no encontrado")

        if cart.status != "abierto":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se puede eliminar un producto de un carrito cerrado")

        product = session.query(Product).get(productId)

        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")

        productCart = session.query(ProductCart).filter(ProductCart.cartId == cartId,ProductCart.productId == productId).first()

        if not productCart:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto en carrito no encontrado")

        sale_cart = session.query(Sale).filter(Sale.cartId == cartId).first()

        if sale_cart:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El carrito se encuentra en una venta")
        
        session.delete(productCart)
        session.commit()
        
    except HTTPException: 
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error al intentar eliminar un producto de un carrito {e}")


