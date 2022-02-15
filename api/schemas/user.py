from api import ma
from api.models.user import UserModel


#       schema        flask-restful
# object ------>  dict ----------> json

#      schema        class Model
# json -------> dict -----------> object


# Сериализация ответа(response)
class UserSchema(ma.SQLAlchemySchema):
    class Meta:
        model = UserModel
        fields = ('id', 'username', "is_staff", "role")


# Десериализация запроса(request)
class UserRequestSchema(ma.SQLAlchemySchema):
    class Meta:
        model = UserModel

    username = ma.Str()
    password = ma.Str()
    role = ma.Str()
    is_staff = ma.Bool()


user_schema = UserSchema()
users_schema = UserSchema(many=True)
