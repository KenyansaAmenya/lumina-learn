from mangum import Mangum
from backend.main import backend

handler = Mangum(backend)