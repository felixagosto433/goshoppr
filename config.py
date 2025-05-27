import os

class Config:
    """
    Base configuration with default settings.
    when other configurations are set, the repeating variables 
    will be overriden with the values of the new class
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
    Currently it matched Staging because we
    dont want to delete the local development. 
    """
    DEBUG = True
    WEAVIATE_CLOUD_URL = os.getenv('WEAVIATE_CLOUD_URL')
    WEAVIATE_ADMIN_KEY = os.getenv('WEAVIATE_ADMIN_KEY') 

class ProductionConfig(Config):
    """
    Configuration for production environment.
    """
    DEBUG = False
    WEAVIATE_CLOUD_URL = os.getenv('WEAVIATE_CLOUD_URL')  # Ensure this is set in production
    WEAVIATE_ADMIN_KEY = os.getenv('WEAVIATE_ADMIN_KEY')  # Ensure this is set in production

class StagingConfig(Config):
    """
    Configuration for staging environment.
    """
    DEBUG = True  # Keep debugging enabled
    WEAVIATE_CLOUD_URL = os.getenv('WEAVIATE_CLOUD_URL')  # Same as production
    WEAVIATE_ADMIN_KEY = os.getenv('WEAVIATE_ADMIN_KEY')  # Same as production


# Mapping configurations to environments
# Mapping configurations to environments
config = {
    'staging': StagingConfig,  # ✅ Added staging configuration
    'production': ProductionConfig,
}
