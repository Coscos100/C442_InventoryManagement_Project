from model import InventoryModel
from werkzeug.security import generate_password_hash

# Create model (DB connection)
model = InventoryModel()

# Input values (you can hardcode or use input())
username = "admin"
password = "admin123"
role = "admin"

# Hash the password
password_hash = generate_password_hash(password)

# Insert into DB
model.create_user(username, password_hash, role)

# Close DB connection
model.close()

print("User created successfully!")