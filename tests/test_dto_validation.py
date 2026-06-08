import pytest
from pydantic import ValidationError


def test_create_instance_from_correct_data():
    """正しいデータからDTOインスタンスが作成できるかをテストする"""
    from app.schemas.dto import NotificationMessage

    msg = NotificationMessage(
        user_id=1,
        line_user_id="U1234567890abcdef",
        listing_url="https://example.com/listing/123",
        contents="新しい物件が見つかりました！",
    )
    assert msg.user_id == 1
    assert msg.line_user_id == "U1234567890abcdef"
    assert msg.listing_url == "https://example.com/listing/123"
    assert msg.contents == "新しい物件が見つかりました！"


def test_valid_required_fields():
    """必須フィールドがかけているとエラーになるかをテストする"""
    from app.schemas.dto import NotificationMessage

    with pytest.raises(ValidationError):
        NotificationMessage(
            line_user_id="U1234567890abcdef",
            listing_url="https://example.com/listing/123",
            contents="新しい物件が見つかりました！",
        )


def test_value_type_validation():
    """フィールドの値の型が正しくないとエラーになるかをテストする"""
    from app.schemas.dto import NotificationMessage

    with pytest.raises(ValidationError):
        NotificationMessage(
            user_id="not_an_int",
            line_user_id="U1234567890abcdef",
            listing_url="https://example.com/listing/123",
            contents="新しい物件が見つかりました！",
        )
