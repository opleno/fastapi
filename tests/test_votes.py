import pytest
from app import models

RIDICULOUSLY_HIGH_NUMBER = 99999


@pytest.fixture
def voted_post(preloaded_posts, session, test_user):
    new_vote = models.Vote(
        post_id=preloaded_posts[3].id, user_id=test_user['id'])
    session.add(new_vote)
    session.commit()


def test_vote_on_post(authenticated_client, preloaded_posts):
    res = authenticated_client.post(
        "/vote/", json={"post_id": preloaded_posts[3].id, "dir": 1})

    assert res.status_code == 201


def test_vote_twice_same_post(authenticated_client, preloaded_posts, voted_post):
    res = authenticated_client.post(
        "/vote/", json={"post_id": preloaded_posts[3].id, "dir": 1})

    assert res.status_code == 409


def test_delete_vote(authenticated_client, preloaded_posts, voted_post):
    res = authenticated_client.post(
        "/vote/", json={"post_id": preloaded_posts[3].id, "dir": 0})

    assert res.status_code == 201


def test_delete__nonexistent_vote(authenticated_client, preloaded_posts):
    res = authenticated_client.post(
        "/vote/", json={"post_id": preloaded_posts[3].id, "dir": 0})

    assert res.status_code == 404


def post_vote_nonexistent_vote(authenticated_client, preloaded_posts):
    res = authenticated_client.post(
        "/vote/", json={"post_id": RIDICULOUSLY_HIGH_NUMBER, "dir": 1})

    assert res.status_code == 404


def post_vote_unauthenticated_user(client, preloaded_posts):
    res = client.post(
        "/vote/", json={"post_id": preloaded_posts[3].id, "dir": 1})

    assert res.status_code == 401
