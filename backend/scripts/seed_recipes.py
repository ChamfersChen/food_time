"""Seed recipe data into the database.

Usage: python -m scripts.seed_recipes
"""
import asyncio
import json
import uuid
from server.database import engine, async_session_factory, Base
from server.models.recipe import Recipe


RECIPES = [
    {
        "name": "番茄炒蛋",
        "description": "家常经典，酸甜可口，5分钟搞定",
        "tags": ["家常", "快手", "下饭"],
        "cuisine": "家常",
        "cook_time": 10,
        "difficulty": "easy",
        "calories": 180,
        "servings": 2,
        "ingredients": [
            {"name": "番茄", "quantity": 2, "unit": "个", "is_essential": True, "aliases": ["西红柿"]},
            {"name": "鸡蛋", "quantity": 3, "unit": "个", "is_essential": True},
            {"name": "大蒜", "quantity": 2, "unit": "瓣", "is_essential": False},
            {"name": "食盐", "quantity": 3, "unit": "克", "is_essential": False},
            {"name": "食用油", "quantity": 15, "unit": "毫升", "is_essential": False},
        ],
        "steps": [
            {"step": 1, "desc": "番茄切块，鸡蛋打散加少许盐搅匀", "duration": 2},
            {"step": 2, "desc": "热锅冷油，倒入蛋液翻炒至凝固盛出", "duration": 2},
            {"step": 3, "desc": "锅中加油，爆香蒜末，倒入番茄翻炒出汁", "duration": 3},
            {"step": 4, "desc": "倒回鸡蛋，加盐调味翻炒均匀即可", "duration": 2},
        ],
        "source": "system",
    },
    {
        "name": "蒜蓉西兰花",
        "description": "清淡健康的快手菜，保留蔬菜本身的清甜",
        "tags": ["家常", "快手", "低卡", "清淡"],
        "cuisine": "家常",
        "cook_time": 8,
        "difficulty": "easy",
        "calories": 85,
        "servings": 2,
        "ingredients": [
            {"name": "西兰花", "quantity": 1, "unit": "颗", "is_essential": True},
            {"name": "大蒜", "quantity": 3, "unit": "瓣", "is_essential": True},
            {"name": "食盐", "quantity": 2, "unit": "克", "is_essential": False},
            {"name": "食用油", "quantity": 10, "unit": "毫升", "is_essential": False},
        ],
        "steps": [
            {"step": 1, "desc": "西兰花切小朵，焯水1分钟捞出沥干", "duration": 3},
            {"step": 2, "desc": "热锅加油，爆香蒜末", "duration": 1},
            {"step": 3, "desc": "倒入西兰花大火翻炒2分钟，加盐调味", "duration": 3},
        ],
        "source": "system",
    },
    {
        "name": "红烧肉",
        "description": "经典家常菜，肉质软糯肥而不腻，配白饭绝妙",
        "tags": ["家常", "下饭", "硬菜"],
        "cuisine": "家常",
        "cook_time": 90,
        "difficulty": "medium",
        "calories": 520,
        "servings": 4,
        "ingredients": [
            {"name": "五花肉", "quantity": 500, "unit": "克", "is_essential": True, "aliases": ["猪肉", "三层肉"]},
            {"name": "生姜", "quantity": 3, "unit": "片", "is_essential": True},
            {"name": "大葱", "quantity": 1, "unit": "根", "is_essential": True},
            {"name": "生抽", "quantity": 30, "unit": "毫升", "is_essential": True},
            {"name": "老抽", "quantity": 15, "unit": "毫升", "is_essential": True},
            {"name": "冰糖", "quantity": 20, "unit": "克", "is_essential": False},
            {"name": "料酒", "quantity": 30, "unit": "毫升", "is_essential": True},
        ],
        "steps": [
            {"step": 1, "desc": "五花肉切3厘米方块，冷水下锅焯水去腥", "duration": 10},
            {"step": 2, "desc": "热锅少油，放冰糖炒出糖色", "duration": 3},
            {"step": 3, "desc": "放入肉块翻炒上色，加料酒、生抽、老抽", "duration": 5},
            {"step": 4, "desc": "加开水没过肉块，大火烧开后转小火炖60分钟", "duration": 60},
            {"step": 5, "desc": "大火收汁至汤汁浓稠即可", "duration": 10},
        ],
        "source": "system",
    },
    {
        "name": "牛油果流心蛋吐司",
        "description": "清晨的能量唤醒，外酥里嫩的完美搭配",
        "tags": ["早餐", "快手", "低卡"],
        "cuisine": "西餐",
        "cook_time": 15,
        "difficulty": "easy",
        "calories": 320,
        "servings": 1,
        "ingredients": [
            {"name": "牛油果", "quantity": 1, "unit": "个", "is_essential": True},
            {"name": "鸡蛋", "quantity": 1, "unit": "个", "is_essential": True},
            {"name": "吐司", "quantity": 2, "unit": "片", "is_essential": True},
            {"name": "食盐", "quantity": 1, "unit": "克", "is_essential": False},
            {"name": "黑胡椒", "quantity": 1, "unit": "克", "is_essential": False},
        ],
        "steps": [
            {"step": 1, "desc": "牛油果对半切开去核，果肉切片", "duration": 3},
            {"step": 2, "desc": "吐司烤至表面微脆，铺上牛油果片", "duration": 5},
            {"step": 3, "desc": "平底锅少油，打入鸡蛋煎至蛋白凝固蛋黄流心", "duration": 4},
            {"step": 4, "desc": "将流心蛋放在吐司上，撒盐和黑胡椒", "duration": 1},
        ],
        "source": "system",
    },
    {
        "name": "清炒时蔬",
        "description": "周末清理冰箱的清爽选择，简单就是幸福",
        "tags": ["家常", "快手", "清淡", "低卡"],
        "cuisine": "家常",
        "cook_time": 8,
        "difficulty": "easy",
        "calories": 65,
        "servings": 2,
        "ingredients": [
            {"name": "菠菜", "quantity": 300, "unit": "克", "is_essential": True, "aliases": ["罗马生菜", "小白菜"]},
            {"name": "大蒜", "quantity": 2, "unit": "瓣", "is_essential": True},
            {"name": "食盐", "quantity": 2, "unit": "克", "is_essential": False},
            {"name": "食用油", "quantity": 10, "unit": "毫升", "is_essential": False},
        ],
        "steps": [
            {"step": 1, "desc": "蔬菜洗净切段，大蒜切末", "duration": 2},
            {"step": 2, "desc": "热锅加油，爆香蒜末", "duration": 1},
            {"step": 3, "desc": "大火快炒蔬菜至变色，加盐调味出锅", "duration": 3},
        ],
        "source": "system",
    },
    {
        "name": "香煎柠檬三文鱼",
        "description": "优质蛋白低脂健康，15分钟搞定的高级感料理",
        "tags": ["快手", "低卡", "健康"],
        "cuisine": "西餐",
        "cook_time": 15,
        "difficulty": "easy",
        "calories": 280,
        "servings": 2,
        "ingredients": [
            {"name": "三文鱼", "quantity": 200, "unit": "克", "is_essential": True, "aliases": ["三文鱼块", "鲑鱼"]},
            {"name": "柠檬", "quantity": 1, "unit": "个", "is_essential": True},
            {"name": "食盐", "quantity": 2, "unit": "克", "is_essential": False},
            {"name": "黑胡椒", "quantity": 1, "unit": "克", "is_essential": False},
            {"name": "橄榄油", "quantity": 10, "unit": "毫升", "is_essential": True},
        ],
        "steps": [
            {"step": 1, "desc": "三文鱼用厨房纸吸干水分，两面撒盐和黑胡椒腌制5分钟", "duration": 7},
            {"step": 2, "desc": "热锅加油，皮朝下煎3分钟至酥脆", "duration": 4},
            {"step": 3, "desc": "翻面再煎2分钟，挤柠檬汁出锅", "duration": 3},
        ],
        "source": "system",
    },
    {
        "name": "奶油蘑菇意面",
        "description": "浓郁奶香的治愈系主食，寒冷天的最佳慰藉",
        "tags": ["西餐", "下饭"],
        "cuisine": "西餐",
        "cook_time": 25,
        "difficulty": "medium",
        "calories": 450,
        "servings": 2,
        "ingredients": [
            {"name": "意面", "quantity": 200, "unit": "克", "is_essential": True},
            {"name": "蘑菇", "quantity": 150, "unit": "克", "is_essential": True, "aliases": ["白蘑菇", "口蘑"]},
            {"name": "淡奶油", "quantity": 100, "unit": "毫升", "is_essential": True},
            {"name": "大蒜", "quantity": 2, "unit": "瓣", "is_essential": True},
            {"name": "食盐", "quantity": 3, "unit": "克", "is_essential": False},
            {"name": "黑胡椒", "quantity": 1, "unit": "克", "is_essential": False},
        ],
        "steps": [
            {"step": 1, "desc": "大锅煮水，加盐下意面煮至al dente", "duration": 10},
            {"step": 2, "desc": "蘑菇切片，热锅加黄油煎至两面金黄", "duration": 5},
            {"step": 3, "desc": "加入蒜末炒香，倒入淡奶油小火煮浓", "duration": 5},
            {"step": 4, "desc": "加入煮好的意面翻拌均匀，撒黑胡椒即可", "duration": 3},
        ],
        "source": "system",
    },
    {
        "name": "皮蛋瘦肉粥",
        "description": "暖胃第一选择，早餐夜宵都适合的经典粥品",
        "tags": ["早餐", "汤类", "治愈"],
        "cuisine": "粤菜",
        "cook_time": 40,
        "difficulty": "easy",
        "calories": 200,
        "servings": 3,
        "ingredients": [
            {"name": "大米", "quantity": 100, "unit": "克", "is_essential": True},
            {"name": "皮蛋", "quantity": 1, "unit": "个", "is_essential": True, "aliases": ["松花蛋"]},
            {"name": "猪肉", "quantity": 100, "unit": "克", "is_essential": True, "aliases": ["瘦肉", "猪瘦肉"]},
            {"name": "生姜", "quantity": 2, "unit": "片", "is_essential": True},
            {"name": "食盐", "quantity": 3, "unit": "克", "is_essential": False},
        ],
        "steps": [
            {"step": 1, "desc": "大米洗净加水，大火煮开转中小火", "duration": 5},
            {"step": 2, "desc": "猪肉切丝用盐和料酒腌制，皮蛋切小块", "duration": 5},
            {"step": 3, "desc": "粥煮至粘稠，加入肉丝和皮蛋煮20分钟", "duration": 20},
            {"step": 4, "desc": "加盐调味，撒葱花出锅", "duration": 2},
        ],
        "source": "system",
    },
    {
        "name": "鸡胸肉沙拉",
        "description": "减脂期的蛋白质补给站，清爽零负担",
        "tags": ["低卡", "快手", "健康"],
        "cuisine": "西餐",
        "cook_time": 15,
        "difficulty": "easy",
        "calories": 220,
        "servings": 1,
        "ingredients": [
            {"name": "鸡胸肉", "quantity": 150, "unit": "克", "is_essential": True},
            {"name": "罗马生菜", "quantity": 100, "unit": "克", "is_essential": True, "aliases": ["生菜"]},
            {"name": "小番茄", "quantity": 5, "unit": "个", "is_essential": True, "aliases": ["圣女果", "番茄"]},
            {"name": "橄榄油", "quantity": 10, "unit": "毫升", "is_essential": True},
            {"name": "柠檬", "quantity": 0.5, "unit": "个", "is_essential": True},
        ],
        "steps": [
            {"step": 1, "desc": "鸡胸肉用盐和黑胡椒腌制，平底锅煎至两面金黄", "duration": 10},
            {"step": 2, "desc": "生菜撕小段，小番茄对半切", "duration": 3},
            {"step": 3, "desc": "鸡胸肉切条，与蔬菜混合，淋上橄榄油和柠檬汁", "duration": 2},
        ],
        "source": "system",
    },
    {
        "name": "番茄牛腩汤",
        "description": "酸甜浓郁的温暖炖菜，配米饭或面包都很绝",
        "tags": ["汤类", "下饭", "硬菜"],
        "cuisine": "家常",
        "cook_time": 120,
        "difficulty": "medium",
        "calories": 380,
        "servings": 4,
        "ingredients": [
            {"name": "牛腩", "quantity": 500, "unit": "克", "is_essential": True, "aliases": ["牛肉"]},
            {"name": "番茄", "quantity": 3, "unit": "个", "is_essential": True, "aliases": ["西红柿"]},
            {"name": "土豆", "quantity": 1, "unit": "个", "is_essential": True},
            {"name": "洋葱", "quantity": 1, "unit": "个", "is_essential": True},
            {"name": "生姜", "quantity": 3, "unit": "片", "is_essential": True},
            {"name": "番茄酱", "quantity": 30, "unit": "克", "is_essential": True},
        ],
        "steps": [
            {"step": 1, "desc": "牛腩切块焯水去血沫，捞出备用", "duration": 15},
            {"step": 2, "desc": "洋葱切块、番茄切块、土豆滚刀块", "duration": 5},
            {"step": 3, "desc": "热锅加油炒香洋葱，加番茄酱翻炒，放入牛腩块", "duration": 5},
            {"step": 4, "desc": "加开水没过食材，大火烧开转小火炖90分钟", "duration": 90},
            {"step": 5, "desc": "加土豆和番茄块继续炖20分钟，调味出锅", "duration": 25},
        ],
        "source": "system",
    },
]


async def seed():
    async with async_session_factory() as db:
        from sqlalchemy import select
        for recipe_data in RECIPES:
            existing = await db.execute(
                select(Recipe).where(Recipe.name == recipe_data["name"], Recipe.source == "system")
            )
            if existing.scalar_one_or_none() is None:
                recipe = Recipe(**recipe_data)
                db.add(recipe)
                print(f"  + {recipe_data['name']}")

        await db.commit()
        print("Seed complete!")


if __name__ == "__main__":
    asyncio.run(seed())