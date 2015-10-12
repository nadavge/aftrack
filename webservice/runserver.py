from aftrack import app
# TODO change after production
from aftrack.config import DevelopmentConfig

app.config.from_object(DevelopmentConfig)

if __name__=="__main__":
	app.run()

