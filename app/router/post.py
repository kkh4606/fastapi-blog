from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import schema, database, models


router = APIRouter(prefix="/posts", tags=["POST"])


@router.post("/", response_model=schema.PostOut)
def create_post(post: schema.PostCreate, db: Session = Depends(database.get_db)):
    new_post = models.Post(**post.model_dump(), owner_id=2)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/")
def get_posts(db: Session = Depends(database.get_db)):
    posts = db.query(models.Post).all()
    return posts


@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(database.get_db)):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found"
        )

    return post


@router.put("/{post_id}")
def update_post(
    post_id: int,
    updated_post: schema.PostUpdate,
    db: Session = Depends(database.get_db),
):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)

    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found"
        )

    post_query.update(updated_post.model_dump(), synchronize_session=False)

    db.commit()

    return post_query.first()


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: Session = Depends(database.get_db)):

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found"
        )
    db.delete(post)
    db.commit()
    return
