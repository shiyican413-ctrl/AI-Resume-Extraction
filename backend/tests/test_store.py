from app.services.store import InMemoryStore


def test_put_resume_uses_unique_ids_for_different_files():
    store = InMemoryStore()

    first = store.put_resume("first.pdf", b"first resume")
    second = store.put_resume("second.pdf", b"second resume")

    assert first.resume_id != second.resume_id
    assert store.get_resume(first.resume_id).file_name == "first.pdf"
    assert store.get_resume(second.resume_id).file_name == "second.pdf"


def test_put_resume_reuses_id_for_identical_file_content():
    store = InMemoryStore()

    first = store.put_resume("first-name.pdf", b"same resume")
    second = store.put_resume("second-name.pdf", b"same resume")

    assert first.resume_id == second.resume_id
    assert second.file_name == "first-name.pdf"
