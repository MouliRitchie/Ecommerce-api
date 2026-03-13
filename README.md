# E-Commerce Backend API

A backend module for a basic e-commerce system built with Django REST Framework. It covers the three core pieces — Products, Cart, and Orders — with real business logic like stock management and atomic order processing.

---

## What's inside

- **Products** — full CRUD, category support, search
- **Cart** — per-user cart, add/update/remove items
- **Orders** — place orders from cart, auto stock deduction, order history
- **Admin panel** — manage everything via Django's built-in admin

---

## Tech Stack

- Python 3.10+
- Django 4.2
- Django REST Framework
- SQLite (no setup needed, works out of the box)

---

## Getting started

**1. Clone the repo**
```bash
git clone https://github.com/MouliRitchie/Ecommerce-api.git
cd Ecommerce-api
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up the database**
```bash
python manage.py makemigrations products cart orders
python manage.py migrate
```

**5. (Optional) Create an admin user**
```bash
python manage.py createsuperuser
```

**6. Run the server**
```bash
python manage.py runserver
```

The API will be live at `http://127.0.0.1:8000/`

---

## API Endpoints

### Products `/api/products/`

| Method | URL | What it does |
|--------|-----|--------------|
| GET | `/api/products/` | List all products |
| POST | `/api/products/` | Add a product |
| GET | `/api/products/<id>/` | Get a single product |
| PUT | `/api/products/<id>/` | Full update |
| PATCH | `/api/products/<id>/` | Partial update |
| DELETE | `/api/products/<id>/` | Delete a product |
| GET | `/api/products/categories/` | List categories |
| POST | `/api/products/categories/` | Create a category |

Supports `?search=<term>` to filter by name, description, or category.

---

### Cart `/api/cart/`

| Method | URL | What it does |
|--------|-----|--------------|
| GET | `/api/cart/?user_identifier=<id>` | View a user's cart |
| POST | `/api/cart/` | Add a product to cart |
| PATCH | `/api/cart/items/<item_id>/` | Update item quantity |
| DELETE | `/api/cart/items/<item_id>/` | Remove an item |
| DELETE | `/api/cart/clear/?user_identifier=<id>` | Clear the entire cart |

---

### Orders `/api/orders/`

| Method | URL | What it does |
|--------|-----|--------------|
| POST | `/api/orders/place/` | Place an order from cart |
| GET | `/api/orders/?user_identifier=<id>` | View order history |
| GET | `/api/orders/<order_id>/` | Get a specific order |
| PATCH | `/api/orders/<order_id>/status/` | Update order status |

---

## How the business logic works

- When an order is placed, **all items are stock-checked first** before anything is saved. If any item is out of stock, the whole order is rejected with a clear error message.
- On a successful order, **stock decreases automatically** for each product.
- If a Pending order is **cancelled**, the stock is automatically restored.
- Adding the same product to the cart twice **increases quantity** instead of creating duplicates.
- Orders **snapshot the product name and price** at the time of purchase, so future price changes don't affect old orders.

---

## Sample requests

**Add a product**
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

**Add to cart**
```json
POST /api/cart/
{
  "user_identifier": "user_123",
  "product_id": 1,
  "quantity": 2
}
```

**Place an order**
```json
POST /api/orders/place/
{
  "user_identifier": "user_123"
}
```

**Update order status**
```json
PATCH /api/orders/1/status/
{
  "order_status": "Completed"
}
```

---

## Testing with Postman

A full Postman collection is included in the repo (`postman_collection.json`).

1. Open Postman → click **Import** → upload `postman_collection.json`
2. Run requests in this order: **Categories → Products → Cart → Orders**

---

## Admin Panel

Visit `http://127.0.0.1:8000/admin/` to manage products, orders, and carts visually. You'll need a superuser account (see setup step 5).
