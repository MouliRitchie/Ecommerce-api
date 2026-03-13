# E-Commerce Backend API

A Django REST Framework backend for a basic e-commerce system with Product management, Cart, and Order processing.

---

## Tech Stack

- Python 3.10+
- Django 4.2
- Django REST Framework 3.14
- SQLite (default, zero-config)

---

## Setup & Run

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd ecommerce_project
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run migrations

```bash
python manage.py migrate
```

### 5. Create a superuser (optional, for Django Admin)

```bash
python manage.py createsuperuser
```

### 6. Start the development server

```bash
python manage.py runserver
```

The API will be available at: `http://127.0.0.1:8000/`

---

## API Endpoints

### Products — `/api/products/`

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/products/` | List all products |
| POST | `/api/products/` | Add a new product |
| GET | `/api/products/<id>/` | Get a single product |
| PUT | `/api/products/<id>/` | Full update a product |
| PATCH | `/api/products/<id>/` | Partial update a product |
| DELETE | `/api/products/<id>/` | Delete a product |
| GET | `/api/products/categories/` | List all categories |
| POST | `/api/products/categories/` | Create a category |

**Query params:** `?search=<term>` — search by name, description, or category.

---

### Cart — `/api/cart/`

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/cart/?user_identifier=<id>` | View cart for a user |
| POST | `/api/cart/` | Add product to cart |
| PATCH | `/api/cart/items/<item_id>/` | Update item quantity |
| DELETE | `/api/cart/items/<item_id>/` | Remove item from cart |
| DELETE | `/api/cart/clear/?user_identifier=<id>` | Clear entire cart |

---

### Orders — `/api/orders/`

| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/orders/place/` | Place order from cart |
| GET | `/api/orders/?user_identifier=<id>` | View order history |
| GET | `/api/orders/<order_id>/` | View a specific order |
| PATCH | `/api/orders/<order_id>/status/` | Update order status |

---

## Business Logic

- **Stock validation**: When placing an order, all items are checked against current stock before any changes are written (atomic transaction).
- **Stock decrement**: On successful order, each product's `stock_quantity` is reduced by the ordered quantity.
- **Stock restore**: If a `Pending` order is cancelled via the status API, stock is automatically restored.
- **Cart persistence**: Adding a product that's already in the cart increases its quantity rather than duplicating.
- **Price snapshot**: Order items capture the product name and price at time of order — price changes won't affect past orders.

---

## Sample Request Bodies

### Add Product
```json
POST /api/products/
{
  "name": "Wireless Headphones",
  "description": "Noise-cancelling over-ear headphones",
  "price": "2999.00",
  "stock_quantity": 50,
  "category": 1
}
```

### Add to Cart
```json
POST /api/cart/
{
  "user_identifier": "user_123",
  "product_id": 1,
  "quantity": 2
}
```

### Place Order
```json
POST /api/orders/place/
{
  "user_identifier": "user_123"
}
```

### Update Order Status
```json
PATCH /api/orders/1/status/
{
  "order_status": "Completed"
}
```

---

## Admin Panel

Visit `http://127.0.0.1:8000/admin/` and log in with your superuser credentials to manage all data visually.

---

## API Testing

Import the included `postman_collection.json` into Postman:
1. Open Postman → Import → Upload `postman_collection.json`
2. Set base URL variable to `http://127.0.0.1:8000`
3. Run requests in order: Categories → Products → Cart → Orders
