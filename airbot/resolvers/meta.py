
from grapher import App
@App.field(
    "meta",
    path = "Query/meta",
    argmap = {
        "/arguments/identity" : "identity"
    }
)
def meta(identity) :
    return "airbotapi 1.0.0"