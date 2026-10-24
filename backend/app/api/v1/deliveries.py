from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.algorithms.dijkstra_routing import DijkstraRouter, build_default_city_graph
from app.core.database import get_db
from app.core.dependencies import require_roles
from app.models.user import User, UserRole
from app.schemas.delivery import (
    DeliveryAgentOut,
    DeliveryAgentUpdate,
    DeliveryAssignmentOut,
    DeliveryAssignRequest,
    RoadEdgeOut,
    RoadGraphData,
    RoadNodeOut,
    RouteResponse,
)
from app.services.delivery_service import DeliveryService

router = APIRouter(prefix="/deliveries", tags=["Delivery & Routing"])


@router.get("/agents", response_model=list[DeliveryAgentOut])
async def list_delivery_agents(db: AsyncSession = Depends(get_db)):
    """List all registered delivery agents with current workloads."""
    return await DeliveryService.get_all_agents(db)


@router.get("/agents/me", response_model=DeliveryAgentOut)
async def get_my_agent_profile(
    current_user: User = Depends(require_roles([UserRole.DELIVERY_AGENT])),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve logged in delivery agent profile."""
    agent = await DeliveryService.get_agent_by_user_id(db, current_user.id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent profile not found."
        )
    return agent


@router.patch("/agents/me/status", response_model=DeliveryAgentOut)
async def update_my_status(
    status_update: DeliveryAgentUpdate,
    current_user: User = Depends(require_roles([UserRole.DELIVERY_AGENT])),
    db: AsyncSession = Depends(get_db),
):
    """Update agent availability or current location node."""
    agent = await DeliveryService.get_agent_by_user_id(db, current_user.id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Agent profile not found."
        )

    if status_update.is_available is not None:
        agent.is_available = status_update.is_available
    if status_update.current_node is not None:
        agent.current_node = status_update.current_node
    if status_update.vehicle_type is not None:
        agent.vehicle_type = status_update.vehicle_type

    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent


@router.post("/assign", response_model=DeliveryAssignmentOut)
async def assign_agent_endpoint(
    req: DeliveryAssignRequest,
    current_user: User = Depends(require_roles([UserRole.RESTAURANT, UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db),
):
    """Triggers greedy assignment + Dijkstra shortest path for an order."""
    assignment = await DeliveryService.assign_agent_to_order(
        db, req.order_id, algorithm_choice=req.preferred_algorithm
    )
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No available delivery agent found or order already assigned/invalid.",
        )
    return assignment


@router.get("/route", response_model=RouteResponse)
async def calculate_arbitrary_route(
    start_node: str = Query(..., description="Origin node ID e.g. Node_R1"),
    end_node: str = Query(..., description="Destination node ID e.g. Node_C1"),
):
    """Computes Dijkstra shortest path and telemetry between any two graph nodes."""
    graph = build_default_city_graph()
    router_inst = DijkstraRouter(graph)
    res = router_inst.shortest_path(start_node, end_node)

    if not res.get("found"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=res.get("error", "No route found between specified nodes."),
        )

    path = res.get("path", [])
    steps = []
    for idx, node in enumerate(path):
        meta = graph.node_metadata.get(node, {})
        steps.append(
            {
                "step_index": idx + 1,
                "node_id": node,
                "label": meta.get("label", node),
                "type": meta.get("node_type", "INTERSECTION"),
                "lat": meta.get("latitude", 0.0),
                "lon": meta.get("longitude", 0.0),
            }
        )

    return RouteResponse(
        order_id=0,
        source_node=start_node,
        destination_node=end_node,
        agent_node=None,
        path=path,
        distance_km=res.get("total_distance_km", 0.0),
        estimated_time_mins=res.get("estimated_time_mins", 0.0),
        steps=steps,
        graph_visual={
            "nodes": [{"id": k, **v} for k, v in graph.node_metadata.items()],
            "edges": [
                {"u": u, "v": v, "w": w}
                for u, neighbors in graph.adj_list.items()
                for v, w in neighbors
                if u < v
            ],
        },
    )


@router.get("/graph", response_model=RoadGraphData)
async def get_road_network_graph():
    """Returns the full city road network topology (nodes and edges)."""
    graph = build_default_city_graph()
    nodes = [
        RoadNodeOut(
            id=node_id,
            label=meta.get("label", node_id),
            node_type=meta.get("node_type", "INTERSECTION"),
            latitude=meta.get("latitude", 0.0),
            longitude=meta.get("longitude", 0.0),
        )
        for node_id, meta in graph.node_metadata.items()
    ]

    edges = []
    seen = set()
    for u, neighbors in graph.adj_list.items():
        for v, w in neighbors:
            edge_key = tuple(sorted([u, v]))
            if edge_key not in seen:
                seen.add(edge_key)
                edges.append(
                    RoadEdgeOut(
                        source_node=u,
                        target_node=v,
                        distance_km=w,
                        traffic_factor=1.0,
                    )
                )

    return RoadGraphData(nodes=nodes, edges=edges)
