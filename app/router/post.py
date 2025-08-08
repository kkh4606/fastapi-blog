from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from .. import schema, database, models, oauth2
from typing import List, Optional
from sqlalchemy import or_


router = APIRouter(prefix="/posts", tags=["POST"])


@router.post("/", response_model=schema.PostOut)
def create_post(
    post: schema.PostCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):

    new_post = models.Post(**post.model_dump(), owner_id=current_user.id)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/", response_model=List[schema.PostOut])
def get_posts(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 10,
):
    query = db.query(models.Post).options(
        joinedload(models.Post.comments), joinedload(models.Post.likes)
    )

    if search:

        query = query.filter(
            or_(
                models.Post.title.ilike(f"%{search}%"),
                models.Post.content.ilike(f"%{search}%"),
            )
        )
    # get total posts

    total = query.count()
    posts = query.offset(skip).limit(limit).all()

    for post in posts:
        post.like_count = len(post.likes)
    return {"total": total, "skip": skip, "limit": limit, "results": posts}


@router.get("/{post_id}")
def get_post(
    post_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
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
    current_user: models.User = Depends(oauth2.get_current_user),
):
    post_query = db.query(models.Post).filter(models.Post.id == post_id)

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
    current_user: models.User = Depends(oauth2.get_current_user),
):

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found"
        )
    db.delete(post)
    db.commit()
    return


@router.post("/like/{post_id}")
def like_post(
    post_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):

    post = db.query(models.Post).filter(models.Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found"
        )

    like_exists = (
        db.query(models.Like)
        .filter(models.Like.user_id == current_user.id, models.Like.post_id == post_id)
        .first()
    )

    if like_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="already liked this post"
        )

    like = models.Like(user_id=current_user.id, post_id=post_id)

    db.add(like)
    db.commit()
    return {"message": "You liked this post"}


@router.post("/comments/{post_id}")
def post_comment(
    post_id: int,
    post_comment: schema.Comment,
    current_user: models.User = Depends(oauth2.get_current_user),
    db: Session = Depends(database.get_db),
):
    post = db.query(models.Post).filter(models.Post.id == post_id).first()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found"
        )

    comment = models.Comment(
        user_id=current_user.id, post_id=post_id, content=post_comment.content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.put("/comments/{comment_id}", response_model=schema.CommentOUt)
def update_comment(
    comment_id: int,
    update_comment: schema.Comment,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="comment not found"
        )

    if comment.user_id != current_user.id:  # type:ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment",
        )

    comment.content = update_comment.content  # type:ignore
    db.commit()
    db.refresh(comment)

    return comment


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(oauth2.get_current_user),
):

    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="comment not found"
        )

    if comment.user_id != current_user.id:  # type:ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment",
        )

    db.delete(comment)
    db.commit()

    return
