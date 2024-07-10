from app_config import create_app
from dotenv import load_dotenv
import redis
# from task import add_numbers


load_dotenv()


app = create_app()

if __name__ == '__main__':
    try:
        # r = redis.Redis(host='redis', port=6379, db=0)
        # redis://default:Speedpay@fintech123!@51.89.226.178/0
        # connect to the redis link above
        r = redis.Redis(
            host="default",
            port=6379,
            password="Speedpay@fintech123!",
            db=0
        )
        print("Connected to Redis very wel")
    except Exception as e:
        print(f"Failed to connect to Redis: {e}")

    #test celery
    # add_numbers.delay(10, 20)
    app.run(debug=True, host='0.0.0.0', port=7000)
