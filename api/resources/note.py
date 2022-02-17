from api import auth, abort, g, Resource, reqparse
from api.models.note import NoteModel
from api.models.tag import TagModel
from api.models.user import UserModel
from api.schemas.note import note_schema, notes_schema, NoteSchema, NoteRequestSchema
from flask_apispec import doc, marshal_with, use_kwargs
from flask_apispec.views import MethodResource
from webargs import fields
from helpers.shortcuts import get_or_404

@doc(tags=["Notes"])
class NoteResource(MethodResource):
    @auth.login_required
    def get(self, note_id):
        """
        Пользователь может получить ТОЛЬКО свою заметку
        """
        author = g.user
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"Note with id={note_id} not found")
        return note_schema.dump(note), 200

    @auth.login_required
    def put(self, note_id):
        """
        Пользователь может редактировать ТОЛЬКО свои заметки
        """
        author = g.user
        parser = reqparse.RequestParser()
        parser.add_argument("text", required=True)
        parser.add_argument("private", type=bool)
        note_data = parser.parse_args()
        note = NoteModel.query.get(note_id)
        if not note:
            abort(404, error=f"note {note_id} not found")
        if note.author != author:
            abort(403, error=f"Forbidden")
        note.text = note_data["text"]

        if note_data.get("private") is not None:
            note.private = note_data.get("private")

        note.save()
        return note_schema.dump(note), 200

    @doc(summary="Delete note", description="Authorized user can archive own notes")
    @auth.login_required
    def delete(self, note_id):
        auth_user = g.user
        note = get_or_404(NoteModel, note_id)
        if note.author_id != auth_user.id:
            abort(403, error=f"Forbidden")
        note.delete()
        return f"Note with id {note_id} was archived", 204 #Ok without body


@doc(tags=["Notes"])
class NotesListResource(MethodResource):

    @doc(summary="Get notes available", description="Get private notes or notes created by authorized user")
    @doc(security=[{"basicAuth": []}])
    @marshal_with(NoteSchema(many=True), code=200)
    @auth.login_required
    def get(self):
        author = g.user
        # notes = NoteModel.query.filter(or_(NoteModel.author_id == author, and_(NoteModel.author_id != author, NoteModel.private is False))).all()
        # print(author.id)
        # notes = NoteModel.query.filter(NoteModel.author_id == author.id).all()
        notes = NoteModel.query.filter(NoteModel.private is False).all()
        # notes = NoteModel.query.all()
        print(notes)
        return notes, 200


    @doc(summary="Create note", description="Create new Note for current auth User")
    @doc(security=[{"basicAuth": []}])
    @doc(responses={400: {"description": 'Bad request'}})
    @marshal_with(NoteSchema, code=201)
    @use_kwargs(NoteRequestSchema, location=("json"))
    @auth.login_required
    def post(self, **kwargs):
        author = g.user
        note = NoteModel(author_id=author.id, **kwargs)
        note.save()
        return note, 201


@doc(tags=["Notes"])
class NoteAddTagResource(MethodResource):
    @doc(summary="Add tags to note")
    @use_kwargs({"tags": fields.List(fields.Int())})
    def put(self, note_id, **kwargs):
        # print("kwargs = ", kwargs)
        note = NoteModel.query.get(note_id)
        # TagModel.query.filter(TagModel.id.in_(kwargs["tags"])).all()
        for tag_id in kwargs["tags"]:
            tag = TagModel.query.get(tag_id)
            note.tags.append(tag)
        note.save()
        return {}

@doc(tags=["Notes"])
class NotesFilterResource(MethodResource):

    # GET: / notes/filter?tags=[tag-1, tag-2, ...]
    @doc(summary="Get notes by tags")
    @marshal_with(NoteSchema(many=True), code=200)
    @use_kwargs({"tags": fields.List(fields.Str())}, location=("query"))
    @use_kwargs({"username": fields.List(fields.Str())}, location=("query"))
    def get(self, **kwargs):
        if "tags" in kwargs.keys():
            notes =  NoteModel.query.join(NoteModel.tags).filter(TagModel.name.in_(kwargs['tags']))
        if "username" in kwargs.keys():
            notes = NoteModel.query.join(NoteModel.author).filter(UserModel.username.in_(kwargs['username']))
        return notes, 200

@doc(tags=["Notes"])
class NoteRestoreResource(MethodResource):
    @doc(summary="Note restore")
    @doc(security=[{"basicAuth": []}])
    @auth.login_required
    def put(self, note_id):
        auth_user = g.user
        note = get_or_404(NoteModel, note_id)
        if note.author_id != auth_user:
            abort(403, error=f"Forbidden")
        note.restore()
        return f"note restored", 200
