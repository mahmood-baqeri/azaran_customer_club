from celery import shared_task
from datetime import datetime



@shared_task
def evaluation():
    try:
        pass
        # evaluation_scoreuser()
    except Exception as e:
        print("خطا در فراخوانی evaluation_scoreuser:", e)

    now = datetime.now()
    print(f"✅ Task 1 executed at {now}")
    # کدهای مربوط به تسک اول


@shared_task
def personnel():
    try:
        pass
        # behko_personnel()
    except Exception as e:
        print("خطا در فراخوانی behko_personnel:", e)

    now = datetime.now()
    print(f"✅ Task 2 executed at {now}")
    # کدهای مربوط به تسک دوم


# @shared_task
# def test():
#     UserScores.objects.get_or_create(
#         status=1,
#         user_id=26,
#         description="test",
#         application="Teest",
#         applicationItem=0,
#         point = 100
#     )
#
#     now = datetime.now()
#     print(f"✅ Task 2 executed at {now}")
#     # کدهای مربوط به تسک دوم

# pip install celery redis

# python -m celery -A bootstrap worker --loglevel=info
# python -m celery -A bootstrap beat --loglevel=info



# sudo apt install redis-server
# supervised systemd
# sudo systemctl restart redis-server
# sudo systemctl status redis-server
# sudo systemctl enable redis-server
# redis-cli
# 127.0.0.1:6379> ping
# PONG
# requirepass yourpassword
# bind 127.0.0.1 ::1
# /etc/redis/redis.conf
#

