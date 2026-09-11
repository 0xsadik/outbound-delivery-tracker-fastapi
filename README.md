Outbound Delivery Tracker API
=============================

A robust, production-ready RESTful API built with **FastAPI** for managing and tracking outbound deliveries, customers, delivery agents, orders, and products.

**Features**
------------

*   **Customer Management:** Maintain and query customer profiles.
    
*   **Product Catalog:** Manage inventory items and product details.
    
*   **Delivery Agents:** Track agent details, availability, and assignments.
    
*   **Delivery Orders:** Create and manage orders linked to customers and products.
    
*   **Deliveries Tracking:** Monitor real-time status and lifecycle of outbound shipments.
    
*   **Interactive Documentation:** Automatic Swagger UI (/docs) and ReDoc (/redoc) generation.
    

**Tech Stack**
--------------

*   **Framework:** FastAPI
    
*   **Database/ORM:** SQLAlchemy
    
*   **Server:** Uvicorn
    
*   **Data Validation:** Pydantic
    

**Project Structure**
---------------------
```
outbound-delivery-tracker-fastapi/
├── app
│   ├── routers
│   │   ├── __init__.py
│   │   ├── customers.py
│   │   ├── deliveries.py
│   │   ├── delivery_agents.py
│   │   ├── delivery_orders.py
│   │   └── products.py
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   └── utils.py
├── README.md
└── requirements.txt
```


    

### **Setup**

```bash

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

```

### Run it 

```bash

uvicorn app.main:app --reload --port 8000

```

### Front-end 

➡️ [here](https://github.com/0xsadik/outbound-delivery-tracker-client) 