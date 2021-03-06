# encoding: utf-8

from web.auth import user
from web.core import Controller, HTTPMethod, request, config
from web.core.locale import _
from web.core.http import HTTPFound, HTTPNotFound, HTTPUnauthorized
from marrow.util.bunch import Bunch

from adam.auth.model.eve import EVECredential
from adam.auth.util.predicate import authorize, authenticated, is_administrator


class CharacterInterface(HTTPMethod):
    def __init__(self, key):
        super(KeyInterface, self).__init__()

        try:
            self.key = EVECredential.objects.get(id=key)
        except EVECredential.DoesNotExist:
            raise HTTPNotFound()

        if self.key.owner.id != user.id:
            raise HTTPUnauthorized()

    def delete(self):
        self.key.delete()

        if request.is_xhr:
            return 'json:', {'success': True}

        raise HTTPFound(location='/key/')


class CharacterList(HTTPMethod):
    @authorize(authenticated)
    def get(self, admin=False):
        if admin and not user.admin:
            raise HTTPUnauthorized("Must be administrative user.")

        return "adam.auth.template.character.list", dict(area='characters', admin=bool(admin), records=user.characters)

    @authorize(authenticated)
    def post(self, **kw):
        data = Bunch(kw)

        record = EVECredential(data.key, data.code, owner=user.id)
        record.save()

	# If record is a character key:
	#   Create character owned by user.id

        if request.is_xhr:
            return 'json:', {'success': True, 'identifier': str(record.id), 'key': record.key, 'code': record.code}

        raise HTTPFound(location='/key/')


class CharacterController(Controller):
    """Entry point for the KEY management RESTful interface."""

    index = CharacterList()

    def __lookup__(self, key, *args, **kw):
        return CharacterInterface(key), args
