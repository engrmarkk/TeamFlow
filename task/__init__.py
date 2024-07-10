from celery import shared_task
# from worker import celery


@shared_task
def add_numbers(x, y):
    print("Adding two numbers")
    return x + y
