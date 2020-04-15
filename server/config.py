class Config(object) :
	SQLALCHEMY_DATABASE_URI = 'sqlite:///data.db'
	SQLALCHEMY_TRACK_MODIFICATIONS = False

	PROPAGATE_EXCEPTIONS = True

	JWT_SECRET_KEY = 'somerandomstring123456789'

	# Swagger.io configuration
	SWAGGER_UI_DOC_EXPANSION = 'list'
	RESTPLUS_MASK_SWAGGER = False