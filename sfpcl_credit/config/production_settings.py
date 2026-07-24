from sfpcl_credit.config.settings import *  # noqa: F403


DEBUG = False
DEPLOYMENT_ENVIRONMENT = "production"
IS_PRODUCTION = True
ENABLE_DEMO_SURFACES = False
INSTALLED_APPS = [  # noqa: F405
    app for app in INSTALLED_APPS if app != "sfpcl_credit.tracer"  # noqa: F405
]
