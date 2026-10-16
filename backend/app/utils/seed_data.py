"""
Database Initial Seeding Utility
--------------------------------
Creates demo accounts for all 4 roles, sample restaurants, menu items, delivery agents, and road network nodes.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.algorithms.dijkstra_routing import build_default_city_graph
from app.core.security import get_password_hash
from app.models.delivery import DeliveryAgent, RoadNode
from app.models.menu import MenuItem
from app.models.restaurant import Restaurant
from app.models.user import User, UserRole


async def seed_initial_data(db: AsyncSession) -> None:
    # 1. Check if already seeded
    stmt = select(User).where(User.email == "admin@fooddelivery.local")
    admin_exists = (await db.execute(stmt)).scalar_one_or_none()
    if admin_exists:
        return

    # 2. Create Users for each Role
    hashed_pwd = get_password_hash("Password123!")
    hashed_admin_pwd = get_password_hash("AdminPassword123!")

    admin = User(
        email="admin@fooddelivery.local",
        username="admin_super",
        hashed_password=hashed_admin_pwd,
        full_name="System Administrator",
        role=UserRole.ADMIN,
        phone="+1-555-0100",
        address="100 Tech HQ Plaza",
        node_id="Node_B",
    )

    rest_owner1 = User(
        email="restaurant@fooddelivery.local",
        username="chef_bistro",
        hashed_password=hashed_pwd,
        full_name="Chef Marco Rossi",
        role=UserRole.RESTAURANT,
        phone="+1-555-0200",
        address="12 Culinary Boulevard",
        node_id="Node_R1",
    )

    rest_owner2 = User(
        email="spicegarden@fooddelivery.local",
        username="chef_priya",
        hashed_password=hashed_pwd,
        full_name="Chef Priya Sharma",
        role=UserRole.RESTAURANT,
        phone="+1-555-0201",
        address="44 Saffron Lane",
        node_id="Node_R2",
    )

    customer1 = User(
        email="customer@fooddelivery.local",
        username="alice_foodie",
        hashed_password=hashed_pwd,
        full_name="Alice Johnson",
        role=UserRole.CUSTOMER,
        phone="+1-555-0301",
        address="Apartment 101, Downtown Tower",
        node_id="Node_C1",
    )

    customer2 = User(
        email="bob@fooddelivery.local",
        username="bob_diner",
        hashed_password=hashed_pwd,
        full_name="Bob Martinez",
        role=UserRole.CUSTOMER,
        phone="+1-555-0302",
        address="Villa 202, Green Park Avenue",
        node_id="Node_C2",
    )

    agent1_user = User(
	email="agent@example.com",
        username="agent_swift",
        hashed_password=hashed_pwd,
        full_name="Sam Swift (Courier 1)",
        role=UserRole.DELIVERY_AGENT,
        phone="+1-555-0401",
        address="North Hub Station",
        node_id="Node_D1",
    )

    agent2_user = User(
        email="agent2@example.com",
        username="agent_turbo",
        hashed_password=hashed_pwd,
        full_name="Taylor Turbo (Courier 2)",
        role=UserRole.DELIVERY_AGENT,
        phone="+1-555-0402",
        address="South Hub Station",
        node_id="Node_D2",
    )

    db.add_all([admin, rest_owner1, rest_owner2, customer1, customer2, agent1_user, agent2_user])
    await db.flush()

    # 3. Create Delivery Agent Profiles
    agent1 = DeliveryAgent(
        user_id=agent1_user.id,
        is_available=True,
        current_node="Node_D1",
        vehicle_type="BIKE",
        rating=4.9,
        current_workload=0,
        max_capacity=4,
        total_deliveries=42,
    )
    agent2 = DeliveryAgent(
        user_id=agent2_user.id,
        is_available=True,
        current_node="Node_D2",
        vehicle_type="SCOOTER",
        rating=4.7,
        current_workload=0,
        max_capacity=4,
        total_deliveries=28,
    )
    db.add_all([agent1, agent2])

    # 4. Create Restaurants
    restaurant1 = Restaurant(
        name="Bistro Gourmet Italiano",
        description="Authentic artisanal Italian pasta, wood-fired pizzas, and fresh Mediterranean salads.",
        cuisine_type="Italian",
        address="12 Culinary Boulevard",
        node_id="Node_R1",
        latitude=12.9716,
        longitude=77.5946,
        rating=4.8,
        is_active=True,
        owner_id=rest_owner1.id,
    )

    restaurant2 = Restaurant(
        name="Spice Garden Royale",
        description="Aromatic curries, tandoori grills, biryanis, and traditional Indian flatbreads.",
        cuisine_type="Indian & Mughlai",
        address="44 Saffron Lane",
        node_id="Node_R2",
        latitude=12.9750,
        longitude=77.5980,
        rating=4.7,
        is_active=True,
        owner_id=rest_owner2.id,
    )

    db.add_all([restaurant1, restaurant2])
    await db.flush()

    # 5. Create Menu Items
    menu_items = [
        # Bistro Items
        MenuItem(
            restaurant_id=restaurant1.id,
            name="Truffle Mushroom Risotto",
            description="Arborio rice cooked with wild forest mushrooms, white truffle oil, and aged Parmigiano-Reggiano.",
            price=18.50,
            category="Main Course",
            is_available=True,
            preparation_time_mins=20,
            image_url="https://images.unsplash.com/photo-1633964913295-ceb43826e7c9?auto=format&fit=crop&w=400&q=80",
        ),
        MenuItem(
            restaurant_id=restaurant1.id,
            name="Margherita Di Bufala Pizza",
            description="San Marzano tomato base, fresh buffalo mozzarella, hand-picked basil, and extra virgin olive oil.",
            price=15.00,
            category="Pizza",
            is_available=True,
            preparation_time_mins=15,
            image_url="https://images.unsplash.com/photo-1604382354936-07c5d9983bd3?auto=format&fit=crop&w=400&q=80",
        ),
        MenuItem(
            restaurant_id=restaurant1.id,
            name="Handmade Tagliatelle Carbonara",
            description="Crisp guanciale, farm-fresh egg yolk, Pecorino Romano, and cracked black pepper.",
            price=16.50,
            category="Pasta",
            is_available=True,
            preparation_time_mins=18,
            image_url="https://images.unsplash.com/photo-1612874742237-6526221588e3?auto=format&fit=crop&w=400&q=80",
        ),
        MenuItem(
            restaurant_id=restaurant1.id,
            name="Classic Tiramisu Classico",
            description="Espresso-soaked ladyfingers layered with creamy mascarpone custard and dusted with Dutch cocoa.",
            price=8.50,
            category="Dessert",
            is_available=True,
            preparation_time_mins=5,
            image_url="https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=400&q=80",
        ),
        # Spice Garden Items
        MenuItem(
            restaurant_id=restaurant2.id,
            name="Hyderabadi Dum Biryani",
            description="Fragrant basmati rice layered with marinated tender spices, saffron, fried onions, and served with mirchi ka salan.",
            price=16.00,
            category="Biryani",
            is_available=True,
            preparation_time_mins=22,
            image_url="https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?auto=format&fit=crop&w=400&q=80",
        ),
        MenuItem(
            restaurant_id=restaurant2.id,
            name="Paneer Butter Masala",
            description="Cubes of cottage cheese cooked in a rich, buttery tomato gravy with fresh cream and kasuri methi.",
            price=13.50,
            category="Main Course",
            is_available=True,
            preparation_time_mins=16,
            image_url="https://images.unsplash.com/photo-1631452180519-c014fe946bc7?auto=format&fit=crop&w=400&q=80",
        ),
        MenuItem(
            restaurant_id=restaurant2.id,
            name="Garlic Butter Naan Basket",
            description="Clay-oven baked fluffy flatbreads brushed with roasted garlic and melted salted butter.",
            price=4.50,
            category="Breads",
            is_available=True,
            preparation_time_mins=8,
            image_url="https://images.unsplash.com/photo-1626777552726-4a6b54c97e46?auto=format&fit=crop&w=400&q=80",
        ),
    ]
    db.add_all(menu_items)

    # 6. Seed Road Network Graph in DB
    graph = build_default_city_graph()
    for node_id, meta in graph.node_metadata.items():
        node = RoadNode(
            id=node_id,
            label=meta.get("label", node_id),
            node_type=meta.get("node_type", "INTERSECTION"),
            latitude=meta.get("latitude", 0.0),
            longitude=meta.get("longitude", 0.0),
        )
        db.add(node)

    await db.commit()
