from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.delivery import DeliveryAgent
from app.models.user import User, UserRole
from app.schemas.user import UserCreate


class UserService:
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email_or_username(db: AsyncSession, identifier: str) -> User | None:
        stmt = select(User).where(or_(User.email == identifier, User.username == identifier))
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
        hashed_pw = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=hashed_pw,
            full_name=user_in.full_name,
            role=user_in.role,
            phone=user_in.phone,
            address=user_in.address,
            node_id=user_in.node_id,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        # If user is a DELIVERY_AGENT, automatically create their agent profile
        if db_user.role == UserRole.DELIVERY_AGENT:
            agent_profile = DeliveryAgent(
                user_id=db_user.id,
                is_available=True,
                current_node=db_user.node_id or "Node_D1",
                vehicle_type="BIKE",
                rating=4.8,
                current_workload=0,
                max_capacity=4,
            )
            db.add(agent_profile)
            await db.commit()

        return db_user

    @staticmethod
    async def authenticate(db: AsyncSession, identifier: str, password: str) -> User | None:
        user = await UserService.get_by_email_or_username(db, identifier)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
