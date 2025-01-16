import os

class Config:
    """
    Base configuration with default settings.
    """
    # Security and general configurations
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')  # Fallback for local development
    DEBUG = False
    TESTING = False

    # Database configurations
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Weaviate configurations (common fallback values can be specified here)
    WEAVIATE_LOCAL_URL = os.getenv('WEAVIATE_LOCAL_URL', 'http://localhost:8080')  # Default for local
    WEAVIATE_CLOUD_URL = os.getenv('WEAVIATE_CLOUD_URL')  # To be fetched from environment variables
    WEAVIATE_ADMIN_KEY = os.getenv('WEAVIATE_ADMIN_KEY')

class DevelopmentConfig(Config):
    """
    Configuration for development environment.
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL', 'sqlite:///dev.db')  # Local SQLite database for dev

class TestingConfig(Config):
    """
    Configuration for testing environment.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL', 'sqlite:///test.db')  # Separate DB for tests

class ProductionConfig(Config):
    """
    Configuration for production environment.
    """
    DEBUG = False
    # Other production settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///production.db'  # Dummy databse uri for now. 
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')  # Production database (PostgreSQL, etc.)
    WEAVIATE_CLOUD_URL = os.getenv('WEAVIATE_CLOUD_URL')  # Ensure this is set in production
    WEAVIATE_ADMIN_KEY = os.getenv('WEAVIATE_ADMIN_KEY')  # Ensure this is set in production

# Mapping configurations to environments
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
