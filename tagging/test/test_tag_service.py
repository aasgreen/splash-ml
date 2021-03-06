import datetime
import pytest

from pymongo.errors import DuplicateKeyError
import mongomock
from ..tag_service import TagService
from ..model import (
    LABEL_NAME,
    SCHEMA_VERSION,
    Asset,
    AssetType,
    Tag,
    Tagger,
    TaggingEvent
)


def json_datetime(unix_timestamp):
    return datetime.datetime.utcfromtimestamp(unix_timestamp).isoformat() + "Z"


@pytest.fixture
def mongodb():
    return mongomock.MongoClient().db
    # return pymongo.MongoClient()


@pytest.fixture
def tag_svc(mongodb):
    return TagService(mongodb)


def test_unique_uid_tag_set(tag_svc: TagService):
    tagger = tag_svc.create_tagger(new_tagger)
    new_tagging_event.tagger_id = tagger.uid
    tagging_event = tag_svc.create_tagging_event(new_tagging_event)
    asset = tag_svc.create_asset(new_asset)
    with pytest.raises(DuplicateKeyError):
        another_tagger = Tagger(**
                {"uid": tagger.uid,
                 "type": "model",
                 "name": "netty"})
        tag_svc.create_tagger(another_tagger)
           
    with pytest.raises(DuplicateKeyError):
        another_event = TaggingEvent(**
            {"uid": tagging_event.uid,
             "tagger_id": tagger.uid,
             "run_time": json_datetime(3),
             "accuracy": 1})
        tag_svc.create_tagging_event(another_event)

    with pytest.raises(DuplicateKeyError):
        another_asset = Asset(**{
            "uid": asset.uid,
            "type": "file",
            "uri": "bar"})
        tag_svc.create_asset(another_asset)


def test_create_and_find_tagger(tag_svc: TagService):
    tagger = tag_svc.create_tagger(new_tagger)
    assert tagger is not None
    return_taggers = tag_svc.find_taggers(name="PyTestNet")
    assert list(return_taggers)[0].name == "PyTestNet"


def test_create_and_find_tagging_event(tag_svc: TagService):
    tagger = tag_svc.create_tagger(new_tagger)
    tagging_event = tag_svc.create_tagging_event(TaggingEvent(tagger_id=tagger.uid, run_time=datetime.datetime.now()))

    return_tagging_event = tag_svc.retrieve_tagging_event(tagging_event.uid)
    assert tagging_event.uid == return_tagging_event.uid
    assert tagging_event.tagger_id == return_tagging_event.tagger_id


def test_create_and_find_asset(tag_svc: TagService):
    tagger = tag_svc.create_tagger(new_tagger)
    new_tagging_event.tagger_id = tagger.uid
    asset = tag_svc.create_asset(new_asset)
    return_asset = tag_svc.retrieve_asset(asset.uid)

    assert return_asset.schema_version == SCHEMA_VERSION

    for tag in asset.tags:
        if tag.name == "geometry":
            assert tag.event_id == "import_id1"

    returns_asset_from_search = list(tag_svc.find_assets(**{"tags.value": "rods"}))[0]
    assert return_asset == returns_asset_from_search, "Search and retrieve return same"


def test_add_asset_tags(tag_svc: TagService):
    asset = tag_svc.create_asset(new_asset)
    tagging_event = tag_svc.create_tagging_event(new_tagging_event)
    new_tag = Tag(**{
            "name": LABEL_NAME,
            "value": "add1",
            "confidence": 0.50,
            "event_id": tagging_event.uid,
    })
    return_asset_set = tag_svc.add_tags([new_tag], asset.uid)

    assert len(return_asset_set.tags) == 4


new_asset = Asset(**{
    "sample_id": "house paint 1234",
    "type": AssetType.file,
    "uri": "images/test.tiff",
    "tags": [
        {
            "name": LABEL_NAME,
            "value": "rods",
            "confidence": 0.9008,
            "event_id": None,
        },
        {
            "name": LABEL_NAME,
            "value": "peaks",
            "confidence": 0.001,

        },
        {
            "name": "geometry",
            "value": "reflection",
            "confidence": 1,
            "event_id": "import_id1",
        }
    ]
})


# name didnt change, though it doesnt carry model_name anymore
new_tagging_event = TaggingEvent(**{
    "tagger_id": "Tricia McMillin",
    "run_time": json_datetime(1134433.223),
    "accuracy": 0.7776
})


new_tagger = Tagger(**{
    "type": "model",
    "name": "PyTestNet",
    "model_info": {
        "label_index": {
            "blue": 1,
            "red": 2
        }
    }
})
