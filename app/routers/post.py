
from fastapi import Response, status, HTTPException, Depends, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from .. import models, schemas, oauth2
from ..database import get_db


router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


@router.get("/", response_model=List[schemas.PostOut])
# TODO: pydantic is trying to validate the response as if the fields of the parent class
# were present at the same level as "Post" and "votes"
# https://www.youtube.com/watch?v=0sOvCWFmrtA&t=37603s
# TEMPORARY FIX: adding default value to PostBase schema
def get_posts(db: Session = Depends(get_db),
              # verifica si esta autenticado:
              current_user=Depends(oauth2.get_current_user),
              # query parameters:
              limit: int = 10,
              skip: int = 0,
              search: Optional[str] = ""
              ):

    # JOIN
    posts_query = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote,
        models.Vote.post_id == models.Post.id,
        isouter=True).group_by(models.Post.id)
    # query params
    posts = posts_query.filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()

    return posts  # schemas.PostOut.from_orm(posts)


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int,
             db: Session = Depends(get_db),
             current_user=Depends(oauth2.get_current_user)):

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote,
        models.Vote.post_id == models.Post.id,
        isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostResponse)
def create_posts(post: schemas.PostCreate,
                 db: Session = Depends(get_db),
                 current_user=Depends(oauth2.get_current_user)):

    # using ** takes out the content of the Post dictionary and transaforms
    # it into what we need:
    # (title=post.title, content=post.content, published=post.published)
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.put("/{id}", response_model=schemas.PostResponse)
def update_post(id: int,
                updated_post: schemas.PostBase,
                db: Session = Depends(get_db),
                current_user=Depends(oauth2.get_current_user)):

    # filter solo construye la query en SQL, por eso se puede reusar en el return
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()

    return post_query.first()


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, description="post succesfully deleted")
def delete_post(id: int,
                db: Session = Depends(get_db),
                current_user=Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} does not exist")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")
    post_query.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
