"""Agent model"""

from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy import String, Text, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from ..database import Base


class AgentStatus(str, enum.Enum):
    """Agent status enum"""

    STOPPED = "stopped"
    RUNNING = "running"
    ERROR = "error"
    STARTING = "starting"


class Agent(Base):
    """Agent model"""

    __tablename__ = "agents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid4().hex)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)
    workspace: Mapped[str] = mapped_column(String(500), nullable=False, default="./workspace")
    agent_dir: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    config: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    status: Mapped[AgentStatus] = mapped_column(
        SQLEnum(AgentStatus), default=AgentStatus.STOPPED
    )
    team_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("teams.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    team: Mapped[Optional["Team"]] = relationship("Team", back_populates="agents")

    def __repr__(self) -> str:
        return f"<Agent {self.name}>"
