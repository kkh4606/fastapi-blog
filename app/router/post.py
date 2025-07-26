from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import model, schema, database, oauth2


router = APIRouter(prefix="/posts", tags=["POST"])


@router.post("/", response_model=schema.PostOut)
def create_post(
    post: schema.PostCreate,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    new_post = model.Post(**post.model_dump(), owner_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/")
def get_posts(
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    posts = db.query(model.Post).all()
    return posts


@router.get("/{post_id}")
def get_post(
    post_id: int,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):
    post = db.query(model.Post).filter(model.Post.id == post_id).first()
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
    current_user: model.User = Depends(oauth2.get_current_user),
):
    post_query = db.query(model.Post).filter(model.Post.id == post_id)

    post = post_query.first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found"
        )

    post_query.update(updated_post.model_dump(), synchronize_session=False)  # type: ignore

    db.commit()

    return post_query.first()


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(database.get_db),
    current_user: model.User = Depends(oauth2.get_current_user),
):

    post = db.query(model.Post).filter(model.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found"
        )
    db.delete(post)
    db.commit()
    return
