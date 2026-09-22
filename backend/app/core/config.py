from pydantic_settings import BaseSettings

class Setting(BaseSettings):
	REDIS_HOST : str = "localhost"
	REDIS_PORT : int = 6379
	REDIS_PASSWORD : str = ""
	APP_ENV : str = "development"

	class Config :
		env_file = ".env"

setting = Setting()

