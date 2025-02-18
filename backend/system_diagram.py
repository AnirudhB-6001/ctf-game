from graphviz import Digraph

dot = Digraph("System Architecture", format="png")

# Components
dot.node("Client", "Client (User)")
dot.node("AuthAPI", "Flask JWT Auth API")
dot.node("DB", "Database (SQLite/PostgreSQL)")
dot.node("Redis", "Redis (Token Blacklist)")

# Requests
dot.edge("Client", "AuthAPI", label="Login / Register")
dot.edge("AuthAPI", "DB", label="Store User")
dot.edge("Client", "AuthAPI", label="Get Access Token")
dot.edge("AuthAPI", "Redis", label="Blacklist Token on Logout")
dot.edge("Client", "AuthAPI", label="Refresh Token")
dot.edge("AuthAPI", "DB", label="Verify User")
dot.edge("Client", "AuthAPI", label="Access Protected Routes")

# Render diagram
dot.render("system_architecture")

print("Diagram saved as system_architecture.png")