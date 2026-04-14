from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models.node import Node
from app.db.models.task import Task
from app.schemas.task import TaskCreate


class TaskService:
    @staticmethod
    def list_tasks(db: Session) -> list[Task]:
        return list(db.scalars(select(Task).order_by(Task.id.desc())).all())

    @staticmethod
    def get_task(db: Session, task_id: int) -> Task | None:
        return db.get(Task, task_id)

    @staticmethod
    def create_task(db: Session, payload: TaskCreate) -> Task:
        if payload.assignment_mode == "manual" and payload.selected_node_id is not None:
            node = db.get(Node, payload.selected_node_id)
            if node is None:
                raise ValueError("selected_node_id에 해당하는 노드가 없습니다.")

        task = Task(
            requester_user_id=payload.requester_user_id,
            prompt=payload.prompt,
            status="pending",
            assignment_mode=payload.assignment_mode,
            selected_node_id=payload.selected_node_id,
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        return task
