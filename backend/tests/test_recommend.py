from server.services.recommend_service import calc_preference_score
from server.models.recipe import Recipe
from server.models.user import User


def test_calc_preference_score_match():
    user = User(
        openid="test",
        nickname="test",
        flavor_pref=["清淡", "微辣"],
    )
    recipe = Recipe(
        name="测试菜",
        tags=["清淡", "快手"],
        cook_time=10,
        difficulty="easy",
        ingredients=[],
        steps=[],
        source="system",
    )
    score = calc_preference_score(recipe, user)
    assert score > 0  # "清淡" overlaps


def test_calc_preference_score_no_match():
    user = User(
        openid="test",
        nickname="test",
        flavor_pref=["特辣"],
    )
    recipe = Recipe(
        name="测试菜",
        tags=["清淡", "快手"],
        cook_time=10,
        difficulty="easy",
        ingredients=[],
        steps=[],
        source="system",
    )
    score = calc_preference_score(recipe, user)
    assert score == 0.0  # No overlap


def test_calc_preference_score_empty_pref():
    user = User(
        openid="test",
        nickname="test",
        flavor_pref=[],
    )
    recipe = Recipe(
        name="测试菜",
        tags=["清淡"],
        cook_time=10,
        difficulty="easy",
        ingredients=[],
        steps=[],
        source="system",
    )
    score = calc_preference_score(recipe, user)
    assert score == 0.5  # Default when no preference