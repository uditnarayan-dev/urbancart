# 🛒 UrbanCart – Django eCommerce Web App

UrbanCart is a full-featured eCommerce web application built with **Django**, offering seamless product browsing, cart management, online payments via **Razorpay**, order placement, and user authentication — all wrapped in a responsive, user-friendly interface.

---

## 🌐 Live Demo
🚀 **Deployed on AWS EC2:**  
http://3.111.130.128:8003/

---

## ✅ Features

| Feature                                      | Status |
|---------------------------------------------|--------|
| User Signup / Login / Logout                | ✅     |
| Product Browsing with Categories            | ✅     |
| Product Details Page                        | ✅     |
| Cart Management (Add/Remove/Update Items)   | ✅     |
| Checkout with Address                       | ✅     |
| Razorpay Payment Integration                | ✅     |
| Order Placement                             | ✅     |
| Order History Tracking                      | ✅     |
| Responsive UI (Bootstrap)                   | ✅     |
| Django Admin Product Management             | ✅     |
| Password Reset via Email                    | ✅     |

---

## 🛠 Tech Stack

| Layer          | Technology     |
|----------------|---------------|
| Backend        | Django         |
| Database       | PostgreSQL     |
| Frontend       | HTML, CSS, Bootstrap |
| Payment Gateway| Razorpay       |
| Environment    | `venv` virtual environment |
| Deployment     | AWS EC2        |

---


---

## 📥 Installation & Local Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/your-username/UrbanCart.git
cd UrbanCart

python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver
```

✅ Visit: http://127.0.0.1:8000/

---
⚡ Razorpay Integration (Payment Flow)
On checkout, users are redirected to Razorpay for secure payment.
After successful payment, the order is created and stored.

---
![Homepage](./app/images/Books.jpg)
![Product Listing](./screenshots/products.png)
![Cart Page](./screenshots/cart.png)
![Checkout](./screenshots/checkout.png)

---
📅 Future Enhancements

✅ Wishlist feature
✅ Coupon/Discount system

✅ Product reviews and rating system
