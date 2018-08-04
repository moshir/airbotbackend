class StoreProxy :
    @classmethod
    def store(cls,store=None) :
        if store is None :
            return cls._store
        else :
            StoreProxy._store = store
            return StoreProxy._store

