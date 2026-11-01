from pydantic_settings import BaseSettings

class Settings(BaseSettings):
	redis_host : str = "localhost"
	redis_port : int = 6379
	redis_password : str = ""
	app_env : str = "development"
	msg_ttl_seconds : int = 3600
	max_msg_length : int = 20000

	class Config :
		env_file = ".env"

settings = Settings()

