# REC Hive

Multi-role campus ordering web app: **Django** (SQLite) backend, **HTML / CSS / vanilla JS** frontend, mobile-first UI with orange accent and bottom navigation on the customer app.

## Project layout

```
REC Hive/
├── backend/                 # Django project (run commands from here)
│   ├── manage.py
│   ├── rec_hive/            # settings, root urls
│   └── apps/
│       ├── users/           # User, Role, Favorite, Notification + auth views/API
│       ├── shops/           # Shop, Category, Product + catalog API
│       ├── cart/            # Cart, CartItem + cart API
│       └── orders/          # Order, OrderItem + ordering API
├── frontend/                # Collected as static files (/static/...)
│   ├── css/
│   ├── js/
│   └── images/
├── templates/               # Django templates (customer, admin, shopkeeper, worker)
├── static/                  # Optional extra static assets
├── media/                   # Created at runtime (uploaded images)
├── db.sqlite3               # Created after migrate (project root)
├── requirements.txt
└── README.md
```

## Quick start

1. Create a virtual environment (recommended), then:

```powershell
cd "path\to\REC Hive\backend"
pip install -r ..\requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

2. Open **http://127.0.0.1:8000/**  
3. Django admin: **http://127.0.0.1:8000/admin/**  

### Demo accounts (after `seed_demo`)

| Role        | Email               | Password   |
|------------|---------------------|------------|
| Admin      | admin@rechive.edu   | admin123   |
| Shopkeeper | shop@rechive.edu    | shop123    |
| Worker     | kitchen@rechive.edu | kitchen123 |
| Customer   | student@rechive.edu | student123 |

Change passwords before any real deployment. Set `DEBUG = False`, a real `SECRET_KEY`, and `ALLOWED_HOSTS` in production.

## API (session + CSRF)

Base path: `/api/`. For mutating requests from the browser, obtain a CSRF cookie via `GET /api/csrf`, then send header `X-CSRFToken` (handled by `frontend/js/api.js`).

| Method | Path | Purpose |
|--------|------|---------|
| POST | `/api/register` | Register (JSON) |
| POST | `/api/login` | Login (JSON, email or phone) |
| POST | `/api/logout` | Logout |
| GET | `/api/me` | Current user |
| PATCH | `/api/profile` | Update profile |
| GET | `/api/shops` | List shops (`?category=&q=`) |
| GET | `/api/shops/<slug>` | Shop detail |
| GET | `/api/products` | List products (`?shop=&category=&popular=1&q=`) |
| GET | `/api/shops/<shop>/products/<slug>` | Product detail |
| GET | `/api/categories` | Categories |
| GET | `/api/cart` | Cart |
| POST | `/api/cart/add` | Add line (`product_id`, `quantity`) |
| POST | `/api/order/create` | Create order from cart |
| GET | `/api/orders` | Customer orders |
| GET | `/api/orders/<id>` | Order detail |
| PATCH | `/api/order/status` | Status update (role rules apply) |
| GET | `/api/orders/all` | Admin / shopkeeper order list |
| GET | `/api/orders/kitchen` | Worker queue |
| … | `/api/admin/*` | Admin users, shops, categories, analytics |
| … | `/api/shopkeeper/products` | Shopkeeper product CRUD |

## Database overview (SQLite)

- **users_role** — `customer`, `admin`, `shopkeeper`, `worker`
- **users_user** — custom user (`email` login), FK → role, `phone`, `is_blocked`
- **shops_category**, **shops_shop** (owner, workers M2M, approval, hours)
- **shops_product** — FK shop, optional category, price, flags
- **cart_cart**, **cart_cartitem** — one cart per user, unique (cart, product)
- **orders_order**, **orders_orderitem** — status workflow, totals, pickup fields
- **users_favorite** — shop and/or product favorites
- **users_notification** — inbox-style notifications

## Portals (URLs)

- Customer: `/home/`, `/outlets/`, `/cart/`, `/checkout/`, `/orders/history/`, `/profile/`, …
- Admin UI: `/admin-panel/` (custom screens; also use Django `/admin/` for data entry)
- Shopkeeper: `/shopkeeper/`
- Kitchen/worker: `/kitchen/`

## Notes

- One order = one shop; the cart rejects mixing outlets until cleared.
- Images: optional; placeholders under `/static/images/placeholder.svg`.
- For production, use PostgreSQL, HTTPS, and a proper static/media setup (`collectstatic`, reverse proxy).
