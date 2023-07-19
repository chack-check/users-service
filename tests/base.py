from datetime import datetime

from app.v1.schemas import DbUser, UserActivities
from app.v1.graphql.graph_types import AuthData, LoginData


AUTH_USER_DATA = AuthData(
    email='test@mail.com',
    username='test',
    phone='88005553535',
    first_name='Ivan',
    last_name='Ivanov',
    password='Password123$',
    password_repeat='Password123$',
)


AUTH_USER_DATA_EXISTS_EMAIL = AuthData(
    email='test@mail.com',
    username='test2',
    phone='89089089089',
    first_name='Ivan',
    last_name='Ivanov',
    password='Password123$',
    password_repeat='Password123$',
)


AUTH_USER_DATA_EXISTS_USERNAME = AuthData(
    email='test2@mail.com',
    username='test',
    phone='89089089089',
    first_name='Ivan',
    last_name='Ivanov',
    password='Password123$',
    password_repeat='Password123$',
)


AUTH_USER_DATA_EXISTS_PHONE = AuthData(
    email='test2@mail.com',
    username='test2',
    phone='88005553535',
    first_name='Ivan',
    last_name='Ivanov',
    password='Password123$',
    password_repeat='Password123$',
)


AUTH_USER_DATA_INVALID_PASSWORDS = AuthData(
    email='test@mail.com',
    username='test',
    phone='88005553535',
    first_name='Ivan',
    last_name='Ivanov',
    password='Password123$',
    password_repeat='Incorrect repeat password',
)


LOGIN_USER_DATA_USERNAME = LoginData(
    phone_or_username='test',
    password='Password123$'
)


LOGIN_USER_DATA_PHONE = LoginData(
    phone_or_username='88005553535',
    password='Password123$'
)


LOGIN_USER_DATA_INCORRECT_USERNAME = LoginData(
    phone_or_username='incorrect',
    password='Password123$'
)


LOGIN_USER_DATA_INCORRECT_PASSWORD = LoginData(
    phone_or_username='test',
    password='incorrect password'
)


TOKEN_USER = DbUser(
    email='test@mail.com',
    username='test',
    phone='88005553535',
    first_name='Ivan',
    last_name='Ivanov',
    password='some_password_hash',
    id=1,
    activity=UserActivities.online,
    last_seen=datetime.utcnow()
)


TOKEN_USER = DbUser(
    email='test@mail.com',
    username='test',
    phone='88005553535',
    first_name='Ivan',
    last_name='Ivanov',
    password='some_password_hash',
    id=1,
    activity=UserActivities.online,
    last_seen=datetime.utcnow()
)


MANY_USERS_DATA = [
    {
        'email': f'test{i}@mail.com',
        'username': f'test{i}',
        'phone': f'880055535{i}',
        'first_name': 'Ivan',
        'last_name': 'Ivanov',
        'password': 'some_password_hash',
    } for i in range(50)
]
