from sqlalchemy.orm import Session

from app.models import Source


def list_all(db: Session, include_archived: bool = False) -> list[Source]:
    q = db.query(Source)
    if not include_archived:
        q = q.filter(Source.archived.is_(False))
    return q.order_by(Source.name).all()


def get(db: Session, source_id: int) -> Source | None:
    return db.query(Source).filter_by(id=source_id).first()


def create(
    db: Session,
    *,
    slug: str,
    name: str,
    kind: str,
    closing_day: int | None = None,
    due_day: int | None = None,
) -> Source:
    src = Source(
        slug=slug,
        name=name,
        kind=kind,
        closing_day=closing_day,
        due_day=due_day,
    )
    db.add(src)
    db.commit()
    db.refresh(src)
    return src


def update_billing(
    db: Session,
    source_id: int,
    *,
    closing_day: int | None,
    due_day: int | None,
) -> Source | None:
    src = get(db, source_id)
    if not src:
        return None
    src.closing_day = closing_day
    src.due_day = due_day
    db.commit()
    db.refresh(src)
    return src


def archive(db: Session, source_id: int) -> None:
    src = get(db, source_id)
    if src:
        src.archived = True
        db.commit()


def unarchive(db: Session, source_id: int) -> None:
    src = get(db, source_id)
    if src:
        src.archived = False
        db.commit()
