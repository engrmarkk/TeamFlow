from app_config import create_app
from dotenv import load_dotenv


load_dotenv()


app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=7000)
