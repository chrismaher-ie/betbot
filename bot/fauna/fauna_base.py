import os

from faunadb import query as q
from faunadb.objects import Ref
from faunadb.client import FaunaClient

from dotenv import load_dotenv

load_dotenv()
FAUNA_KEY = os.getenv('FAUNA_KEY')

client = FaunaClient(secret=FAUNA_KEY)