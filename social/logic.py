import datetime

from django.core.cache import cache

from common import keys
from social.models import Swipe, Friend
from swiper import config
from user.models import User


def like(uid, sid):
    Swipe.like(uid, sid)
    if Swipe.has_like_me(sid, uid):
        uid1, uid2 = (uid, sid) if uid < sid else (sid, uid)
        Friend.make_friends(uid1=uid1, uid2=uid2)
        return True
    return False


def superlike(uid, sid):
    Swipe.superlike(uid, sid)
    if Swipe.has_like_me(sid, uid):
        uid1, uid2 = (uid, sid) if uid < sid else (sid, uid)
        Friend.make_friends(uid1=uid1, uid2=uid2)
        return True
    return False


def get_rcmd_list(user):
    """
    :return: [user1, user2, user2]
    """
    # 已经滑过的人不能再滑
    swiped_list = Swipe.objects.filter(uid=user.id).only('sid')
    sid_list = [s.sid for s in swiped_list]
    # 推荐用户中不能出现自己
    sid_list.append(user.id)

    current_year = datetime.datetime.now().year
    min_birth_year = current_year - user.profile.max_dating_age
    max_birth_year = current_year - user.profile.min_dating_age
    users = User.objects.filter(location=user.profile.location,
                        birth_year__range=(min_birth_year, max_birth_year),
                        sex=user.profile.dating_sex).exclude(id__in=sid_list)[:20]
    return users


def rewind(user):
    now = datetime.datetime.now()
    key = keys.REWIND_KEY % now.date()
    rewind_times = cache.get(key, 0)  # 取不到给一个默认值0
    if rewind_times < config.REWIND_TIMES:
        # 可以执行反悔操作.
        # 删除最近的滑动记录.
        record = Swipe.objects.filter(uid=user.id).latest(field_name='time')
        # 判断是否有好友关系
        uid1, uid2 = (user.id, record.sid) if user.id < record.sid else(
        record.sid, user.id)
        friends = Friend.objects.filter(uid1=uid1, uid2=uid2)
        friends.delete()
        record.delete()

        # 更新缓存中的反悔次数
        rewind_times += 1
        timeout = 86400 - (now.hour * 60 * 60 + now.minute * 60 + now.second)
        cache.set(key, rewind_times, timeout)
        return True
    else:
        return False
