
from fastapi.templating import Jinja2Templates
import os

# Initialize templates
# We assume the templates directory is at app/templates
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates"))
