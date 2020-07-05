from pypinfo import db

CREDS_FILE = '/path/to/creds_file.json'


def test_get_credentials(tmp_path):
    # Arrange
    db.DB_FILE = str(tmp_path / 'db.json')  # Mock

    # Assert
    assert db.get_credentials() is None


def test_set_credentials(tmp_path):
    # Arrange
    db.DB_FILE = str(tmp_path / 'db.json')  # Mock

    # Act
    db.set_credentials(CREDS_FILE)


def test_set_credentials_twice(tmp_path):
    # Arrange
    db.DB_FILE = str(tmp_path / 'db.json')  # Mock

    # Act
    db.set_credentials(CREDS_FILE)
    db.set_credentials(CREDS_FILE)


def test_round_trip(tmp_path):
    # Arrange
    db.DB_FILE = str(tmp_path / 'db.json')  # Mock

    # Act
    db.set_credentials(CREDS_FILE)

    # Assert
    assert db.get_credentials() == CREDS_FILE


def test_get_credentials_table(tmp_path):
    db.DB_FILE = str(tmp_path / 'db.json')
    with db.get_credentials_table() as table:
        assert not table._storage._handle.closed
        with db.get_credentials_table(table) as table2:
            assert table2 is table
        assert not table._storage._handle.closed
    assert table._storage._handle.closed
