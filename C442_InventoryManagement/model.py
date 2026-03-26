import mysql.connector
from config import DB_CONFIG
from flask_login import UserMixin


class User(UserMixin):
    """
    Flask-Login user object.

    UserMixin gives us:
    - is_authenticated
    - is_active
    - is_anonymous
    - get_id()

    We still store our own fields like username and role.
    """
    def __init__(self, user_id, username, password_hash, role):
        # Flask-Login expects an id attribute
        self.id = str(user_id)

        # Store username for display and app logic
        self.username = username

        # Store hashed password from DB
        self.password_hash = password_hash

        # Store role for authorization
        self.role = role


class InventoryModel:
    def __init__(self):
        """
        Create a database connection and dictionary cursor.

        dictionary=True makes rows come back like:
        row["Username"]
        instead of tuple indexes like row[0]
        """
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor(dictionary=True)

    # -----------------------------
    # Product methods
    # -----------------------------

    def get_all_products(self):
        """
        Return all products from the Product table.
        """
        self.cursor.execute("SELECT * FROM Product")
        return self.cursor.fetchall()

    def get_product(self, name):
        """
        Search for products whose Name contains the search text.
        """
        self.cursor.execute(
            "SELECT * FROM Product WHERE Name LIKE %s",
            (f"%{name}%",)
        )
        return self.cursor.fetchall()

    def add_product(self, name, price, quantity, category):
        """
        Insert a new product row.
        """
        sql = """
        INSERT INTO Product (Name, Price, Quantity, Category)
        VALUES (%s, %s, %s, %s)
        """
        self.cursor.execute(sql, (name, price, quantity, category))
        self.conn.commit()
        return self.cursor.lastrowid

    def update_product(self, product_id, name, price, quantity, category):
        """
        Update an existing product by ProductId.
        """
        sql = """
        UPDATE Product
        SET Name = %s, Price = %s, Quantity = %s, Category = %s
        WHERE ProductId = %s
        """
        self.cursor.execute(sql, (name, price, quantity, category, product_id))
        self.conn.commit()
        return self.cursor.rowcount

    def delete_product(self, product_id):
        """
        Delete a product by ProductId.
        """
        self.cursor.execute(
            "DELETE FROM Product WHERE ProductId = %s",
            (product_id,)
        )
        self.conn.commit()
        return self.cursor.rowcount

    # -----------------------------
    # User methods
    # -----------------------------

    def get_user_by_id(self, user_id):
        """
        Get one user row by UserId.

        Flask-Login uses this during session loading.
        """
        self.cursor.execute(
            "SELECT * FROM User WHERE UserId = %s",
            (user_id,)
        )
        return self.cursor.fetchone()

    def get_user_by_username(self, username):
        """
        Get one user row by Username.

        Used during login when a username is submitted.
        """
        self.cursor.execute(
            "SELECT * FROM User WHERE Username = %s",
            (username,)
        )
        return self.cursor.fetchone()

    def create_user(self, username, password_hash, role):
        """
        Insert a new user into the User table.

        password_hash should already be hashed before calling this.
        """
        sql = """
        INSERT INTO User (Username, PasswordHash, Role)
        VALUES (%s, %s, %s)
        """
        self.cursor.execute(sql, (username, password_hash, role))
        self.conn.commit()
        return self.cursor.lastrowid

    def build_user_object(self, row):
        """
        Convert a DB row into a Flask-Login User object.

        This is useful so your auth code does not need to keep rebuilding
        the same object manually.
        """
        if not row:
            return None

        return User(
            user_id=row["UserId"],
            username=row["Username"],
            password_hash=row["PasswordHash"],
            role=row["Role"]
        )

    def close(self):
        """
        Close cursor and connection explicitly.
        """
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def __del__(self):
        """
        Fallback cleanup if object is destroyed.

        It is better to call close() explicitly when possible.
        """
        try:
            self.close()
        except:
            pass

    def get_quantity_by_category(self):
        self.cursor.execute("""
                            SELECT Category, SUM(Quantity) AS total
                            FROM Product
                            GROUP BY Category
                            """)
        return self.cursor.fetchall()