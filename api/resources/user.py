from api import Resource, abort, reqparse, auth
from api.models.user import UserModel
from api.schemas.user import user_schema, users_schema, UserSchema, UserRequestSchema
from api.schemas.note import NoteSchema
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, use_kwargs, doc
from webargs import fields
from flask_babel import _


@doc(description='Api for notes.', tags=['Users'])
class UserResource(MethodResource):
    @marshal_with(UserSchema, code=200)
    def get(self, user_id):
        # language=YAML
        """
        Get User by id
        ---
        tags:
            - Users
        parameters:
             - in: path
               name: user_id
               type: integer
               required: true
               default: 1
        responses:
            200:
                description: A single user item
                schema:
                    id: User
                    properties:
                       id:
                           type: integer
                           description: user id
                           default: 1
                       username:
                           type: string
                           description: The name of the user
                           default: Steven Wilson
                       is_staff:
                           type: boolean
                           description: user is staff
                           default: false
                      role:
                           type: string
                           description: ....
                           default: simple_user
        """
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, error=f"User with id={user_id} not found")
        return user, 200

    @doc(summary="Change user data")
    @use_kwargs(UserRequestSchema, location=('json'))
    @marshal_with(UserSchema, code=200)
    @auth.login_required(role="admin")
    def put(self, user_id, **kwargs):
        user = UserModel.query.get(user_id)
        if kwargs.get("user"):
            user.username = kwargs["username"]
        if kwargs.get("role"):
            user.role = kwargs["role"]
        if kwargs.get("is_staff"):
            user.is_staff = kwargs["is_staff"]
        user.save()
        return user, 200

    @auth.login_required
    def delete(self, user_id):
        user = UserModel.query.get(user_id)
        if not user:
            abort(404, error=f"User with id={user_id} not found")
        user.delete()
        return (f"user has been deleted", 200)



@doc(description='Api for notes.', tags=['Users'])
class UsersListResource(MethodResource):
    @doc(summary="Get users list")
    @marshal_with(UserSchema(many=True), code=200)
    def get(self):
        users = UserModel.query.all()
        return users, 200

    @doc(summary="New user register", description="Create new user")
    @doc(responses={400: {"description": "Data is not enough or user already exists"}})
    @use_kwargs(UserRequestSchema, location=('json'))
    @marshal_with(UserSchema, code=201)
    def post(self, **kwargs):
        user = UserModel(**kwargs)
        user.save()
        if not user.id:
            # abort(400, error=f"User with username:{user.username} already exists")
            abort(404, error=_("User with username %(username)s already exists", username=user.username, id=user.id))  # Flask Babel syntaxis.
        return user, 201

@doc(tags=['Users'])
class UserNotesResource(MethodResource):
    @doc(summary="Get notes by user")
    @marshal_with(NoteSchema(many=True), code=200)
    def get(self, user_id):
        notes = UserModel.query.get(user_id).notes.all()
        return notes, 200