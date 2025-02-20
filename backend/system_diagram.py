from graphviz import Digraph

dot = Digraph("System Architecture", format="png")

# Components
dot.node("Client", "Client (User)")
dot.node("FlaskAPI", "Flask API (Main App)")
dot.node("Auth", "Auth Module")
dot.node("Challenges", "Challenges Module")
dot.node("DB", "Database (SQLite/PostgreSQL)")
dot.node("Redis", "Redis (Token Blacklist)")
dot.node("JWT", "JWT Manager")
dot.node("Models", "Models (User, Challenge)")
dot.node("RBAC", "Role-Based Access Control")

# Client Requests
dot.edge("Client", "FlaskAPI", label="User Requests (Login, Register, Play Game)")

# Auth Flow
dot.edge("FlaskAPI", "Auth", label="Handles Login & Tokens")
dot.edge("Auth", "DB", label="Fetch User & Password Hash")
dot.edge("Auth", "JWT", label="Generate Access/Refresh Token")
dot.edge("Auth", "Redis", label="Blacklist Token on Logout")

# Challenges API
dot.edge("FlaskAPI", "Challenges", label="Fetch Challenges")
dot.edge("Challenges", "DB", label="Retrieve Challenge Data")

# Protected API Calls
dot.edge("Client", "FlaskAPI", label="Access Protected Routes")
dot.edge("FlaskAPI", "JWT", label="Verify Access Token")
dot.edge("JWT", "Redis", label="Check Token Blacklist")
dot.edge("JWT", "RBAC", label="Enforce Role-Based Access")

# Models
dot.edge("Auth", "Models", label="Uses User Model")
dot.edge("Challenges", "Models", label="Uses Challenge Model")

# Render diagram
dot.render("detailed_system_architecture")

print("Detailed diagram saved as detailed_system_architecture.png")
