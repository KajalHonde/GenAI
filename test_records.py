from app.records import count_by, filter_records, get_by_id, load_records, search

R = load_records()


def test_twenty_records():
    assert len(R) == 20


def test_counts():
    assert count_by(R, "hazard") == {"flood": 7, "heatwave": 7, "earthquake": 6}


def test_search_and_id():
    assert search(R, "ORS")
    assert get_by_id(R, 1)["hazard"] == "flood"
    assert get_by_id(R, 999) is None


def test_filter():
    dont_flood = filter_records(R, hazard="flood", do_or_dont="dont")
    assert [r["id"] for r in dont_flood] == [7]
    assert all(r["phase"].startswith("during") for r in filter_records(R, hazard="earthquake", phase="during"))
