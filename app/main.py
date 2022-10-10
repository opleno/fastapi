from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


# Connection to DB
counter = 1
while True:
    try:
        conn = psycopg2.connect(host='ec2-99-81-137-11.eu-west-1.compute.amazonaws.com',
                                database='d5onrb4mv9gm9a', user='mtxncvrblsauxo', password='password',
                                cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Connected succesfully to the DB")
        break
    except Exception as error:
        print("NOT Connected to the DB")
        print("Error: ", error)
        if counter <= 32:
            counter = counter * 2
        time.sleep(counter)


my_posts = [{"title": "title of post 1",
             "content": "content of post 1", "id": 1}, {"title": "favorite foods", "content": "I like pizza", "id": 2}]



def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i


@app.get("/")
def root():
    return {"message": "Hello World"}


# POSTS CRUD

@app.get("/posts")
def get_posts():
    cursor.execute('SELECT * FROM posts ')
    posts = cursor.fetchall()
    return {"data": posts}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    cursor.execute(' SELECT * FROM posts WHERE id=%s ', (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")
    return {"post_detail": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    # SQL statement must not use string f"". It must use %s to let psycopg2 sanitize the input (stop SQL injections)
    cursor.execute(
        'INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *', 
        (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"data": new_post}


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute('UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING *', 
        (post.title, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} does not exist")
    return {"data": updated_post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT, description="post succesfully deleted")
def delete_post(id: int):
    cursor.execute('DELETE FROM posts WHERE id=%s RETURNING *', (str(id)))
    deleted_post = cursor.fetchone()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post {id} does not exist")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
