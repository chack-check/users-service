from datetime import datetime

from app.v1.schemas import DbUser, UserActivities
from app.v1.graphql.graph_types import AuthData


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
