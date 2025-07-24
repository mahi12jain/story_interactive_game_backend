# import os
# from dotenv import load_dotenv

# # Load environment variables
# load_dotenv()

# class Config:
#     """Base configuration class"""
    
#     # Database Configuration
#     DATABASE_URL = os.getenv('URL_DATABASE', 'postgresql://postgres:root@localhost:5432/Gaming')
    
#     # Convert PostgreSQL URL to async version for asyncpg
#     @property
#     def DATABASE_URL_ASYNC(self):
#         return self.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
    
#     # Sync version for migrations and some operations
#     @property
#     def DATABASE_URL_SYNC(self):
#         return self.DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://')
    
#     # SQLAlchemy Configuration
#     SQLALCHEMY_TRACK_MODIFICATIONS = False
#     SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
#     # Database Pool Configuration
#     POOL_SIZE = int(os.getenv('POOL_SIZE', '10'))
#     MAX_OVERFLOW = int(os.getenv('MAX_OVERFLOW', '20'))
#     POOL_TIMEOUT = int(os.getenv('POOL_TIMEOUT', '30'))
#     POOL_RECYCLE = int(os.getenv('POOL_RECYCLE', '3600'))
    
#     # Legacy support for SQLALCHEMY_ENGINE_OPTIONS
#     @property
#     def SQLALCHEMY_ENGINE_OPTIONS(self):
#         return {
#             'pool_pre_ping': True,
#             'pool_recycle': self.POOL_RECYCLE,
#             'pool_size': self.POOL_SIZE,
#             'max_overflow': self.MAX_OVERFLOW,
#             'pool_timeout': self.POOL_TIMEOUT
#         }
    
#     # Application Configuration
#     DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
#     SECRET_KEY = os.getenv('SECRET_KEY', 'ndfnsdfksaopasdnvsdk64545234xkcnsd856y5')
    
#     # API Configuration
#     API_V1_STR = "/api/v1"
#     PROJECT_NAME = os.getenv('PROJECT_NAME', 'Gaming API')
    
#     # CORS Configuration
#     BACKEND_CORS_ORIGINS = os.getenv('BACKEND_CORS_ORIGINS', '*').split(',')
    
#     # Pagination
#     DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', '20'))
#     MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', '100'))

# class DevelopmentConfig(Config):
#     """Development configuration"""
#     DEBUG = True
#     SQLALCHEMY_ECHO = True

# class ProductionConfig(Config):
#     """Production configuration"""
#     DEBUG = False
#     SQLALCHEMY_ECHO = False
    
#     # Override with more conservative pool settings for production
#     @property
#     def SQLALCHEMY_ENGINE_OPTIONS(self):
#         return {
#             'pool_pre_ping': True,
#             'pool_recycle': 3600,
#             'pool_size': 5,
#             'max_overflow': 10,
#             'pool_timeout': 30
#         }

# class TestingConfig(Config):
#     """Testing configuration"""
#     TESTING = True
#     DATABASE_URL = os.getenv('TEST_DATABASE_URL', 'postgresql://postgres:root@localhost:5432/Gaming_test')

# # Configuration dictionary
# config_by_name = {
#     'development': DevelopmentConfig,
#     'production': ProductionConfig,
#     'testing': TestingConfig
# }

# # Get configuration based on environment
# def get_config():
#     config_name = os.getenv('FLASK_ENV', 'development')
#     config_class = config_by_name.get(config_name, DevelopmentConfig)
#     return config_class()

# # Create a global settings instance that can be imported
# settings = get_config()

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Database Configuration
    DATABASE_URL = os.getenv('URL_DATABASE', 'postgresql://postgres:root@localhost:5432/Gaming')
    
    # Convert PostgreSQL URL to async version for asyncpg
    @property
    def DATABASE_URL_ASYNC(self):
        return self.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://')
    
    # Sync version for migrations and some operations
    @property
    def DATABASE_URL_SYNC(self):
        return self.DATABASE_URL.replace('postgresql://', 'postgresql+psycopg2://')
    
    # SQLAlchemy Configuration
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', 'False').lower() == 'true'
    
    # Database Pool Configuration
    POOL_SIZE = int(os.getenv('POOL_SIZE', '10'))
    MAX_OVERFLOW = int(os.getenv('MAX_OVERFLOW', '20'))
    POOL_TIMEOUT = int(os.getenv('POOL_TIMEOUT', '30'))
    POOL_RECYCLE = int(os.getenv('POOL_RECYCLE', '3600'))
    
    # Legacy support for SQLALCHEMY_ENGINE_OPTIONS
    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self):
        return {
            'pool_pre_ping': True,
            'pool_recycle': self.POOL_RECYCLE,
            'pool_size': self.POOL_SIZE,
            'max_overflow': self.MAX_OVERFLOW,
            'pool_timeout': self.POOL_TIMEOUT
        }
    
    # Application Configuration
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'ndfnsdfksaopasdnvsdk64545234xkcnsd856y5')
    
    # JWT Configuration
    ALGORITHM = os.getenv('ALGORITHM', 'HS256')
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7'))
    
    # API Configuration
    API_V1_STR = "/api/v1"
    PROJECT_NAME = os.getenv('PROJECT_NAME', 'Gaming API')
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS = os.getenv('BACKEND_CORS_ORIGINS', '*').split(',')
    
    # Pagination
    DEFAULT_PAGE_SIZE = int(os.getenv('DEFAULT_PAGE_SIZE', '20'))
    MAX_PAGE_SIZE = int(os.getenv('MAX_PAGE_SIZE', '100'))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    # You can override JWT settings for development if needed
    # ACCESS_TOKEN_EXPIRE_MINUTES = 60  # Longer expiry for development

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    # More secure JWT settings for production
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '15'))  # Shorter expiry for production
    
    # Override with more conservative pool settings for production
    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self):
        return {
            'pool_pre_ping': True,
            'pool_recycle': 3600,
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30
        }

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_URL = os.getenv('TEST_DATABASE_URL', 'postgresql://postgres:root@localhost:5432/Gaming_test')
    # Short expiry for testing
    ACCESS_TOKEN_EXPIRE_MINUTES = 5

# Configuration dictionary
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig
}

# Get configuration based on environment
def get_config():
    config_name = os.getenv('FLASK_ENV', 'development')
    config_class = config_by_name.get(config_name, DevelopmentConfig)
    return config_class()

# Create a global settings instance that can be imported
settings = get_config()