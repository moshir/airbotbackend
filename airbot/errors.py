

class ApplicationAlreadyExists(Exception) :
    pass

class ObjectNotFound(Exception) :
    pass


class DuplicateError(Exception) :
    pass


class ProgrammingError(Exception) :
    pass



class MissingParameter(Exception):
    pass


class InvalidParameter(Exception):
    pass


class BucketAlreayExists(Exception):
    pass

class AddGroupError(Exception) :
    pass


class InvalidAwsAccount(Exception):
    pass


class GlueDatabaseCreationError(Exception) :
    pass


class GlueTableDeletionError(Exception) :
    pass


class GlueTableCreationError(Exception) :
    pass


class InvalidDatasetColumns (Exception) :
    pass