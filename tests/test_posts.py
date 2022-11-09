from typing import List
from app import schemas


def test_get_all_posts(authenticated_client, test_post_posts):
    res = authenticated_client.get("/posts/")

    def validate(post):
        return schemas.PostOut(**post)

    posts_map = map(validate, res.json())
    posts_list = list(posts_map)

    assert len(res.json()) == len(test_post_posts)
    assert res.status_code == 200


def test_unauthenticated_user_get_all_posts(client, test_post_posts):
    res = client.get("/posts/")
    assert res.status_code == 401


def test_unauthenticated_user_get_post(client, test_post_posts):
    res = client.get(f"/posts/{test_post_posts[0].id}")
    assert res.status_code == 401


def test_get_nonexistent_post(authenticated_client):
    res = authenticated_client.get(f"/posts/99999")
    assert res.status_code == 404


def test_get_post(authenticated_client, test_post_posts):
    res = authenticated_client.get(f"/posts/{test_post_posts[0].id}")
    post = schemas.PostOut(**res.json())
    assert post.Post.id == test_post_posts[0].id
    assert post.Post.content == test_post_posts[0].content
    assert post.Post.title == test_post_posts[0].title