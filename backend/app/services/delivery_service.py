from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.algorithms.dijkstra_routing import DijkstraRouter, build_default_city_graph
from app.algorithms.greedy_assignment import GreedyAgentSelector
from app.models.delivery import DeliveryAgent, DeliveryAssignment
from app.models.order import Order


class DeliveryService:
    @staticmethod
    async def get_all_agents(db: AsyncSession) -> list[DeliveryAgent]:
        stmt = select(DeliveryAgent).options(selectinload(DeliveryAgent.user))
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_agent_by_id(db: AsyncSession, agent_id: int) -> DeliveryAgent | None:
        stmt = (
            select(DeliveryAgent)
            .where(DeliveryAgent.id == agent_id)
            .options(selectinload(DeliveryAgent.user))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_agent_by_user_id(db: AsyncSession, user_id: int) -> DeliveryAgent | None:
        stmt = (
            select(DeliveryAgent)
            .where(DeliveryAgent.user_id == user_id)
            .options(selectinload(DeliveryAgent.user))
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def assign_agent_to_order(
        db: AsyncSession,
        order_id: int,
        algorithm_choice: str = "GREEDY_HEURISTIC",
    ) -> DeliveryAssignment | None:
        """
        Executes Greedy Agent Assignment + Dijkstra Route Computation for an order.
        """
        # Fetch order with restaurant
        stmt = select(Order).where(Order.id == order_id).options(selectinload(Order.restaurant))
        result = await db.execute(stmt)
        order = result.scalar_one_or_none()

        if not order:
            return None

        restaurant_node = order.restaurant.node_id if order.restaurant else "Node_R1"
        customer_node = order.delivery_node or "Node_C1"

        # Check for existing assignment
        stmt_assign = select(DeliveryAssignment).where(DeliveryAssignment.order_id == order_id)
        existing_assign = (await db.execute(stmt_assign)).scalar_one_or_none()
        if existing_assign:
            return existing_assign

        # Get candidate agents
        agents = await DeliveryService.get_all_agents(db)
        if not agents:
            return None

        # Build candidate dictionaries
        agent_dicts = [
            {
                "id": a.id,
                "user_id": a.user_id,
                "current_node": a.current_node,
                "current_workload": a.current_workload,
                "max_capacity": a.max_capacity,
                "rating": a.rating,
                "is_available": a.is_available,
            }
            for a in agents
        ]

        selector = GreedyAgentSelector()
        best_candidate, _ = selector.select_best_agent(restaurant_node, agent_dicts)

        if not best_candidate:
            return None

        chosen_agent_id = best_candidate["agent_id"]
        chosen_agent_node = best_candidate["current_node"]
        score = best_candidate["composite_score"]

        # Calculate Dijkstra Route: Agent -> Restaurant -> Customer
        city_graph = build_default_city_graph()
        router = DijkstraRouter(city_graph)

        leg1 = router.shortest_path(chosen_agent_node, restaurant_node)
        leg2 = router.shortest_path(restaurant_node, customer_node)

        leg1_path = leg1.get("path", [chosen_agent_node, restaurant_node])
        leg2_path = leg2.get("path", [restaurant_node, customer_node])
        full_path = leg1_path + leg2_path[1:]

        total_distance = round(
            leg1.get("total_distance_km", 0.0) + leg2.get("total_distance_km", 0.0), 2
        )
        total_time = round(
            leg1.get("estimated_time_mins", 0.0) + leg2.get("estimated_time_mins", 0.0), 1
        )

        assignment = DeliveryAssignment(
            order_id=order.id,
            agent_id=chosen_agent_id,
            algorithm_used=algorithm_choice,
            assignment_score=score,
            route_path=full_path,
            total_distance=total_distance,
            estimated_time_mins=total_time,
            notes=f"Assigned via {algorithm_choice}. Score: {score}. Multi-leg: {chosen_agent_node}->{restaurant_node}->{customer_node}",
        )
        db.add(assignment)

        # Update agent workload
        chosen_agent = await db.get(DeliveryAgent, chosen_agent_id)
        if chosen_agent:
            chosen_agent.current_workload += 1
            db.add(chosen_agent)

        await db.commit()
        await db.refresh(assignment)
        return assignment
