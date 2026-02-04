import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi import HTTPException
import httpx


@pytest.mark.asyncio
async def test_borrow_book_success(borrow_modules, mock_db_session):
    service = borrow_modules.service
    user_id = 1
    book_id = 1

    # Mock external API validations
    # We use AsyncMock because the service functions are async and awaited
    with patch(
        "service.validate_user_via_api", new_callable=AsyncMock
    ) as mock_validate_user:
        with patch(
            "service.validate_book_via_api", new_callable=AsyncMock
        ) as mock_validate_book:
            with patch(
                "service.update_book_availability_via_api", new_callable=AsyncMock
            ) as mock_update_book:
                result = await service.borrow_book(mock_db_session, book_id, user_id)

                assert result.user_id == user_id
                assert result.book_id == book_id
                assert result.returned_at is None

                mock_validate_user.assert_called_once_with(user_id)
                mock_validate_book.assert_called_once_with(book_id)
                mock_update_book.assert_called_once_with(book_id, False)

                mock_db_session.add.assert_called_once()
                mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_borrow_book_user_not_found(borrow_modules, mock_db_session):
    service = borrow_modules.service

    with patch(
        "service.validate_user_via_api",
        side_effect=HTTPException(status_code=404),
        new_callable=AsyncMock,
    ):
        with pytest.raises(HTTPException) as exc:
            await service.borrow_book(mock_db_session, 1, 1)
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_borrow_book_book_not_found(borrow_modules, mock_db_session):
    service = borrow_modules.service

    with patch("service.validate_user_via_api", new_callable=AsyncMock):
        with patch(
            "service.validate_book_via_api",
            side_effect=HTTPException(status_code=404),
            new_callable=AsyncMock,
        ):
            with pytest.raises(HTTPException) as exc:
                await service.borrow_book(mock_db_session, 1, 1)
            assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_return_book_success(borrow_modules, mock_db_session):
    service = borrow_modules.service
    models = borrow_modules.models

    user_id = 1
    book_id = 1

    mock_record = models.BorrowRecord(
        id=1, user_id=user_id, book_id=book_id, returned_at=None
    )

    # Mock db.execute(select(...))
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = mock_record
    mock_db_session.execute.return_value = mock_result

    with patch("service.validate_user_via_api", new_callable=AsyncMock):
        with patch(
            "service.update_book_availability_via_api", new_callable=AsyncMock
        ) as mock_update_book:
            result = await service.return_book(mock_db_session, book_id, user_id)

            assert result.returned_at is not None
            mock_update_book.assert_called_once_with(book_id, True)
            mock_db_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_return_book_no_active_record(borrow_modules, mock_db_session):
    service = borrow_modules.service

    # Mock db.execute(select(...)) returning None
    mock_result = MagicMock()
    mock_result.scalars.return_value.first.return_value = None
    mock_db_session.execute.return_value = mock_result

    with patch("service.validate_user_via_api", new_callable=AsyncMock):
        with pytest.raises(HTTPException) as exc:
            await service.return_book(mock_db_session, 1, 1)
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_validate_user_via_api_success(borrow_modules):
    service = borrow_modules.service

    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        await service.validate_user_via_api(1)
        mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_validate_user_via_api_not_found(borrow_modules):
    service = borrow_modules.service

    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        with pytest.raises(HTTPException) as exc:
            await service.validate_user_via_api(1)
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_validate_user_via_api_error(borrow_modules):
    service = borrow_modules.service

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        with pytest.raises(HTTPException) as exc:
            await service.validate_user_via_api(1)
        assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_validate_user_via_api_unavailable(borrow_modules):
    service = borrow_modules.service

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.side_effect = httpx.RequestError("Error")

        with pytest.raises(HTTPException) as exc:
            await service.validate_user_via_api(1)
        assert exc.value.status_code == 503


@pytest.mark.asyncio
async def test_validate_book_via_api_success(borrow_modules):
    service = borrow_modules.service

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"is_available": True}

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        await service.validate_book_via_api(1)
        mock_client.get.assert_called_once()


@pytest.mark.asyncio
async def test_validate_book_via_api_not_available(borrow_modules):
    service = borrow_modules.service

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"is_available": False}

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        with pytest.raises(HTTPException) as exc:
            await service.validate_book_via_api(1)
        assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_validate_book_via_api_not_found(borrow_modules):
    service = borrow_modules.service

    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.return_value = mock_response

        with pytest.raises(HTTPException) as exc:
            await service.validate_book_via_api(1)
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_validate_book_via_api_unavailable(borrow_modules):
    service = borrow_modules.service

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.get.side_effect = httpx.RequestError("Error")

        with pytest.raises(HTTPException) as exc:
            await service.validate_book_via_api(1)
        assert exc.value.status_code == 503


@pytest.mark.asyncio
async def test_update_book_availability_via_api_success(borrow_modules):
    service = borrow_modules.service

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True}

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.patch.return_value = mock_response

        await service.update_book_availability_via_api(1, False)
        mock_client.patch.assert_called_once()


@pytest.mark.asyncio
async def test_update_book_availability_via_api_not_found(borrow_modules):
    service = borrow_modules.service

    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.patch.return_value = mock_response

        with pytest.raises(HTTPException) as exc:
            await service.update_book_availability_via_api(1, False)
        assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_book_availability_via_api_error(borrow_modules):
    service = borrow_modules.service

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Error"

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.patch.return_value = mock_response

        with pytest.raises(HTTPException) as exc:
            await service.update_book_availability_via_api(1, False)
        assert exc.value.status_code == 500


@pytest.mark.asyncio
async def test_update_book_availability_via_api_unavailable(borrow_modules):
    service = borrow_modules.service

    with patch("httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client
        mock_client.patch.side_effect = httpx.RequestError("Error")

        with pytest.raises(HTTPException) as exc:
            await service.update_book_availability_via_api(1, False)
        assert exc.value.status_code == 503
