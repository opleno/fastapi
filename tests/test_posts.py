import pytest
from typing import List
from app import schemas

RIDICULOUSLY_HIGH_NUMBER = 99999


def test_get_all_posts(authenticated_client, preloaded_posts):
    res = authenticated_client.get("/posts/")

    def validate(post):
        return schemas.PostOut(**post)

    posts_map = map(validate, res.json())
    posts_list = list(posts_map)

    assert len(res.json()) == len(preloaded_posts)
    assert res.status_code == 200


def test_unauthenticated_user_get_all_posts(client, preloaded_posts):
    res = client.get("/posts/")
    assert res.status_code == 401


def test_unauthenticated_user_get_post(client, preloaded_posts):
    res = client.get(f"/posts/{preloaded_posts[0].id}")
    assert res.status_code == 401


def test_get_nonexistent_post(authenticated_client):
    res = authenticated_client.get(f"/posts/{RIDICULOUSLY_HIGH_NUMBER}")
    assert res.status_code == 404


def test_get_post(authenticated_client, preloaded_posts):
    res = authenticated_client.get(f"/posts/{preloaded_posts[0].id}")
    post = schemas.PostOut(**res.json())

    assert post.Post.id == preloaded_posts[0].id
    assert post.Post.content == preloaded_posts[0].content
    assert post.Post.title == preloaded_posts[0].title


@pytest.mark.parametrize("title, content, published", [
    ("awesome new title", "awesome new content", True),
    ("favorite pizza", "I love vegan pepperoni", False),
    ("hello", "content 3", True),
])
def test_create_post(authenticated_client, test_user, title, content, published):
    res = authenticated_client.post(
        "/posts/", json={"title": title, "content": content, "published": published})
    created_post = schemas.PostResponse(**res.json())

    assert res.status_code == 201
    assert created_post.title == title
    assert created_post.content == content
    assert created_post.published == published
    assert created_post.owner_id == test_user['id']


def test_create_post_default_published(authenticated_client, test_user):
    res = authenticated_client.post(
        "/posts/", json={"title": "title123", "content": "content123"})
    created_post = schemas.PostResponse(**res.json())

    assert res.status_code == 201
    assert created_post.title == "title123"
    assert created_post.content == "content123"
    assert created_post.published == True
    assert created_post.owner_id == test_user['id']


def test_unauthenticated_user_post_post(client, preloaded_posts):
    res = client.post(
        "/posts/", json={"title": "title123", "content": "content123"})
    assert res.status_code == 401


def test_unauthenticated_user_delete_post(client, preloaded_posts):
    res = client.delete(f"/posts/{preloaded_posts[0].id}")
    assert res.status_code == 401


def test_delete_post(authenticated_client, preloaded_posts):
    res = authenticated_client.delete(f"/posts/{preloaded_posts[0].id}")
    assert res.status_code == 204


def test_delete_nonexistent_post(authenticated_client, preloaded_posts):
    res = authenticated_client.delete(f"/posts/{RIDICULOUSLY_HIGH_NUMBER}")
    assert res.status_code == 404


def test_delete_other_users_post(authenticated_client, preloaded_posts):
    res = authenticated_client.delete(f"/posts/{preloaded_posts[3].id}")

    assert res.status_code == 403
