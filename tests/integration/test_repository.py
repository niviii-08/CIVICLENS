from backend.repositories.common import source_repo

def test_crud_source(db_session):
    """
    Test generic repository capabilities using the isolated db_session fixture.
    """
    source_in = {"name": "Test Repository Source", "type": "Test", "url": "http://test.repo"}
    source = source_repo.create(db_session, obj_in=source_in)
    assert source.id is not None
    assert source.name == "Test Repository Source"
    
    fetched_source = source_repo.get(db_session, id=source.id)
    assert fetched_source is not None
    assert fetched_source.id == source.id
    
    update_in = {"name": "Updated Repo Source", "type": "Updated Test"}
    updated_source = source_repo.update(db_session, db_obj=fetched_source, obj_in=update_in)
    assert updated_source.name == "Updated Repo Source"
    
    refetched_source = source_repo.get(db_session, id=source.id)
    assert refetched_source.name == "Updated Repo Source"
    
    source_repo.create(db_session, obj_in={"name": "Second Source", "type": "Test"})
    sources = source_repo.get_multi(db_session, limit=10)
    assert len(sources) >= 2
    
    deleted_source = source_repo.remove(db_session, id=source.id)
    assert deleted_source.id == source.id
    
    missing_source = source_repo.get(db_session, id=source.id)
    assert missing_source is None
