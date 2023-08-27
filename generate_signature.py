from argparse import ArgumentParser, Namespace
import hmac
import hashlib
from pathlib import Path
import sys

from dotenv import dotenv_values


BASE_DIR = Path(__file__).parent


def parse_args() -> Namespace:
    parser = ArgumentParser(
        description="Signature for sending verification code generator"
    )
    parser.add_argument("-s", "--secret", required=False)
    parser.add_argument("-d", "--data", required=True)
    return parser.parse_args()


def parse_dotenv() -> dict[str, str]:
    return dotenv_values(BASE_DIR / '.env.dev')


def get_secret_key(args: Namespace) -> str:
    if args.secret:
        return args.secret

    dotenv_secret = parse_dotenv().get('USERS_SERVICE_SECRET_KEY')
    if dotenv_secret:
        return dotenv_secret

    print(
        "You need to specify secret key as `-s` or `--s` parameter "
        f"or specify it in {BASE_DIR / '.env.dev'} file as "
        "`USERS_SERVICE_SECRET_KEY` var"
    )
    sys.exit()


def main():
    args = parse_args()
    secret_key = get_secret_key(args)
    print(hmac.new(
        secret_key.encode(), args.data.encode(), hashlib.sha256
    ).hexdigest())


if __name__ == '__main__':
    main()

