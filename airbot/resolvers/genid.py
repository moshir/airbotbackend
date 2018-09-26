from hashids import Hashids
from uuid import uuid4
from datetime import datetime
class ID :
    alphabet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'

    @classmethod
    def now(cls):
        return datetime.now().strftime("%Y%m%d%H%M%S")

    @classmethod
    def get(cls):
        hashids = Hashids(min_length=16, alphabet=ID.alphabet)
        return hashids.encode(int(cls.now()))






if __name__ == "__main__" :
    print ID.get()



