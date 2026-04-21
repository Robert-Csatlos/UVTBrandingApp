from auth import get_password_hash

my_password = "superadmin"
hashed = get_password_hash(my_password)

print(f"Your hashed password is:\n{hashed}")