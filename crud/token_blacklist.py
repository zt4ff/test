from typing import List, Union

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from models.token_blacklist import TokenBlacklist


class TokenBlacklistCRUD:
    @staticmethod
    def get_token(db: Session, token: str) -> Union[TokenBlacklist, None]:
        token = db.scalar(select(TokenBlacklist).where(TokenBlacklist.token == token))
        return token

    @staticmethod
    def add_token(db: Session, token: str) -> TokenBlacklist:
        new_token = TokenBlacklist(token=token)
        db.add(new_token)
        db.commit()
        db.refresh(new_token)
        return new_token

    @staticmethod
    def add_tokens(db: Session, tokens: List[str]):
        for token in tokens:
            new_token = TokenBlacklist(token=token)
            db.add(new_token)

        db.commit()

        return True


token_blacklist_crud = TokenBlacklistCRUD()
