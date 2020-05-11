from app.models import Admin, Realm, User, Badge, UserBadges
import random
from colormap import rgb2hex

def calculate_avg_completed(realm):
    users = realm.users.all()
    number_of_badges = realm.badges.count()
    number_of_users = realm.users.count()

    if number_of_badges == 0 or number_of_users == 0:
        return 0

    finished = 0

    for user in users:
        badges = user.badges.all()
        for badge in badges:
            if badge.finished:
                finished += 1

    return ( finished / (number_of_users * number_of_badges) ) * 100


def generate_colors(n):
    ret = []
    r = int(random.random() * 256)
    g = int(random.random() * 256)
    b = int(random.random() * 256)
    if n != 0:
        step = 256 / n
    else:
        step = 0
    for i in range(n):
        r += step
        g += step
        b += step
        r = int(r) % 256
        g = int(g) % 256
        b = int(b) % 256
        ret.append(rgb2hex(r,g,b)) 
    return ret

def get_levels(realm):
    users = realm.users.all()
    levels = []
    for user in users:
        levels.append(user.level)

    users_per_level = [(level, levels.count(level)) for level in set(levels)]

    colors = generate_colors(len(users_per_level))

    res = [(item[0][0], item[0][1], item[1]) for item in zip(users_per_level, colors)]

    return res

def get_badge_completion(realm):
    users = realm.users.all()
    ids_badges = []
    for user in users:
        badges = user.badges.all()
        for badge in badges:
            if badge.finished:
                ids_badges.append(badge.id_badge)

    badges = realm.badges.all()

    colors = generate_colors(len(badges))

    association = [(badge.name, ids_badges.count(badge.id_badge)) for badge in set(badges)]

    res = [(item[0][0], item[0][1], item[1]) for item in zip(association, colors)]

    return res
