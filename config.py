import os

class Config:
    """
    Base configuration with default settings.
    """
    # Security and general configurations
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')  # Fallback for local development
    DEBUG = False
    TESTING = False

    # Weaviate configurations (common fallback values can be specified here)
    WEAVIATE_LOCAL_URL = os.getenv('WEAVIATE_LOCAL_URL', 'http://localhost:8080')  # Default for local
    WEAVIATE_CLOUD_URL = os.getenv('WEAVIATE_CLOUD_URL')  # To be fetched from environment variables
    WEAVIATE_ADMIN_KEY = os.getenv('WEAVIATE_ADMIN_KEY')


class DevelopmentConfig(Config):
    """
    Configuration for development environment.
    """
    DEBUG = True


class TestingConfig(Config):
    """
    Configuration for testing environment.
    """
    TESTING = True


class ProductionConfig(Config):
    """
    Configuration for production environment.
    """
    DEBUG = False
    WEAVIATE_CLOUD_URL = os.getenv('WEAVIATE_CLOUD_URL')  # Ensure this is set in production
    WEAVIATE_ADMIN_KEY = os.getenv('WEAVIATE_ADMIN_KEY')  # Ensure this is set in production


# Mapping configurations to environments
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
