from re import T
from typing import Optional
from fastapi import Body, FastAPI, Response, status, HTTPException
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
    rating: Optional[int] = None

MAX_ATTEMPTS = 3
for attempt in range(MAX_ATTEMPTS+1):
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="fastapi",
            user="postgres",
            password="fastapi22",
            cursor_factory=RealDictCursor # Make sure that return the columns names as keys
        )
        cursor = conn.cursor()
        print("Connected to Postgres successfully")
        break
    except Exception as error:
        print("Error while connecting to Postgres: ")
        print("Error: ", error)
        time.sleep(2)
    if attempt == MAX_ATTEMPTS:
        raise HTTPException(status_code=500, detail="Error while connecting to Database")


@app.get("/")
async def root():
    return {"message": "Welcome to my asdasdAPI"}


@app.get("/posts")
def get_posts():
    cursor.execute("SELECT * FROM posts")
    posts = cursor.fetchall()
    return {"data":  posts}


@app.get("/posts/{post_id}")
def get_post(post_id: int):
    cursor.execute("SELECT * FROM posts WHERE id = %s", (str(post_id)))
    post = cursor.fetchone()
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {post_id} does not exist")
    return {"data": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute("INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *", (post.title, post.content, post.published))
    conn.commit()
    post = cursor.fetchone()
    return {"data": post}

# delete a post by id
@app.delete("/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int):
    cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (str(post_id)))
    conn.commit()
    deleted_post = cursor.fetchone()
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {post_id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{post_id}", status_code=status.HTTP_200_OK)
def update_post(post_id: int, post: Post):
    cursor.execute("UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *"
                    , (post.title, post.content, post.published, str(post_id)))
    conn.commit()
    updated_post = cursor.fetchone()
    if not updated_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {post_id} does not exist")
    return {"data": updated_post}
