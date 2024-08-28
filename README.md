# Project Structure and Setup

## Folder Structure

```
stihl_scraper/
│
├── .env                  # Environment variables (sensitive data)
├── .gitignore            # Git ignore file
├── requirements.txt      # Python dependencies
├── README.md             # Project documentation
│
├── app/
│   ├── main.py           # FastAPI application entry point
│   ├── auth.py           # Authentication module
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── database.py   # Database connection and session
│   │   └── product.py    # SQLAlchemy models
│   │
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── controller.py # Main controller logic
│   │
│   ├── views/
│   │   ├── __init__.py
│   │   └── ui.py         # View logic (Excel, JSON export)
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── products.py   # Product-related routes
│   │   └── scraper.py    # Scraper-related routes
│   │
│   └── static/
│       └── index.html    # Frontend dashboard
│
└── tests/
    ├── __init__.py
    ├── test_auth.py
    ├── test_controller.py
    └── test_models.py
```

## Setup Instructions

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```
     source venv/bin/activate
     ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following content:
   ```
   DB_USERNAME=your_mysql_username
   DB_PASSWORD=your_mysql_password
   DB_HOST=your_mysql_host
   DB_NAME=your_database_name
   SECRET_KEY=your_secret_key_for_jwt
   GOOGLE_SHEET_ID=your_google_sheet_id
   ```

5. Update the `main.py` file to use environment variables:
   ```python
   from dotenv import load_dotenv
   import os

   load_dotenv()

   # Use environment variables
   db_url = f"mysql://{os.getenv('DB_USERNAME')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
   SECRET_KEY = os.getenv('SECRET_KEY')
   ```

6. Add `.env` to your `.gitignore` file to prevent sensitive data from being committed:
   ```
   echo ".env" >> .gitignore
   echo "venv/" >> .gitignore
   ```

7. Initialize a git repository (if not already done):
   ```
   git init
   ```

8. Make your initial commit:
   ```
   git add .
   git commit -m "Initial commit"
   ```

Remember to never commit your `.env` file to version control. Each developer should have their own local `.env` file with their specific configuration.