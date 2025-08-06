import sys
import os

# Add your project directory to the sys.path
sys.path.insert(0, '/home/yourusername/mysite')

from app import create_app

application = create_app()

if __name__ == "__main__":
    application.run()