import os
from dotenv import load_dotenv


class Config:
    """Configuration class to store environment variables"""

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "5000"))
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

    def __repr__(self):
        return f"Config(HOST={self.HOST}, PORT={self.PORT}, OPENAI_API_KEY={'***' if self.OPENAI_API_KEY else 'Not Set'})"


# Global config instance
config = Config()


def create_folders():
    """
    Creates the necessary folder structure for the car rental website.
    Creates folders if they don't already exist.
    """
    # Define the folder structure
    folders = ["images", "images/cars", "public", "src", "src/api"]

    # Create each folder
    for folder in folders:
        folder_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Created folder: {folder}")
        else:
            print(f"Folder already exists: {folder}")
