from api import abort
from flask_babel import _


def get_or_404(model, id):
    obj = model.query.get(id)
    if not obj:
        # abort(404, error=f"{model.__name__} with id={id} not found")
        abort(404, error=_("%(model)s with id=%(id)s not found", model=model.__name__, id=id))  # Flask Babel syntaxis.
    return obj
