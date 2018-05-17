import json

import pytest
from django.core.files.base import ContentFile
from django.urls import reverse

from leaflet_storage.models import DataLayer, Map

from .base import MapFactory

pytestmark = pytest.mark.django_db


@pytest.fixture
def post_data():
    return {
        "name": 'name',
        "display_on_load": True,
        "rank": 0,
        "geojson": '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[-3.1640625,53.014783245859235],[-3.1640625,51.86292391360244],[-0.50537109375,51.385495069223204],[1.16455078125,52.38901106223456],[-0.41748046875,53.91728101547621],[-2.109375,53.85252660044951],[-3.1640625,53.014783245859235]]]},"properties":{"_storage_options":{},"name":"Ho god, sounds like a polygouine"}},{"type":"Feature","geometry":{"type":"LineString","coordinates":[[1.8017578124999998,51.16556659836182],[-0.48339843749999994,49.710272582105695],[-3.1640625,50.0923932109388],[-5.60302734375,51.998410382390325]]},"properties":{"_storage_options":{},"name":"Light line"}},{"type":"Feature","geometry":{"type":"Point","coordinates":[0.63720703125,51.15178610143037]},"properties":{"_storage_options":{},"name":"marker he"}}],"_storage":{"displayOnLoad":true,"name":"new name","id":1668,"remoteData":{},"color":"LightSeaGreen","description":"test"}}'  # noqa
    }


def test_get(client, settings, datalayer):
    url = reverse('datalayer_view', args=(datalayer.pk, ))
    response = client.get(url)
    if getattr(settings, 'LEAFLET_STORAGE_XSENDFILE_HEADER', None):
        assert response['ETag'] is not None
    assert response['Last-Modified'] is not None
    assert response['Cache-Control'] is not None
    assert 'Content-Encoding' not in response
    j = json.loads(response.content.decode())
    assert '_storage' in j
    assert 'features' in j
    assert j['type'] == 'FeatureCollection'


def test_update(client, datalayer, map, post_data):
    url = reverse('datalayer_update', args=(map.pk, datalayer.pk))
    client.login(username=map.owner.username, password="123123")
    name = 'new name'
    rank = 2
    post_data['name'] = name
    post_data['rank'] = rank
    response = client.post(url, post_data, follow=True)
    assert response.status_code == 200
    modified_datalayer = DataLayer.objects.get(pk=datalayer.pk)
    assert modified_datalayer.name == name
    assert modified_datalayer.rank == rank
    # Test response is a json
    j = json.loads(response.content.decode())
    assert "id" in j
    assert datalayer.pk == j['id']


def test_should_not_be_possible_to_update_with_wrong_map_id_in_url(client, datalayer, map, post_data):  # noqa
    other_map = MapFactory(owner=map.owner)
    url = reverse('datalayer_update', args=(other_map.pk, datalayer.pk))
    client.login(username=map.owner.username, password="123123")
    name = 'new name'
    post_data['name'] = name
    response = client.post(url, post_data, follow=True)
    assert response.status_code == 403
    modified_datalayer = DataLayer.objects.get(pk=datalayer.pk)
    assert modified_datalayer.name == datalayer.name


def test_delete(client, datalayer, map):
    url = reverse('datalayer_delete', args=(map.pk, datalayer.pk))
    client.login(username=map.owner.username, password='123123')
    response = client.post(url, {}, follow=True)
    assert response.status_code == 200
    assert not DataLayer.objects.filter(pk=datalayer.pk).count()
    # Check that map has not been impacted
    assert Map.objects.filter(pk=map.pk).exists()
    # Test response is a json
    j = json.loads(response.content.decode())
    assert 'info' in j


def test_should_not_be_possible_to_delete_with_wrong_map_id_in_url(client, datalayer, map):  # noqa
    other_map = MapFactory(owner=map.owner)
    url = reverse('datalayer_delete', args=(other_map.pk, datalayer.pk))
    client.login(username=map.owner.username, password='123123')
    response = client.post(url, {}, follow=True)
    assert response.status_code == 403
    assert DataLayer.objects.filter(pk=datalayer.pk).exists()


def test_get_gzipped(client, datalayer, settings):
    url = reverse('datalayer_view', args=(datalayer.pk, ))
    response = client.get(url, HTTP_ACCEPT_ENCODING='gzip')
    if getattr(settings, 'LEAFLET_STORAGE_XSENDFILE_HEADER', None):
        assert response['ETag'] is not None
    assert response['Last-Modified'] is not None
    assert response['Cache-Control'] is not None
    assert response['Content-Encoding'] == 'gzip'


def test_optimistic_concurrency_control_with_good_etag(client, datalayer, map, post_data):  # noqa
    # Get Etag
    url = reverse('datalayer_view', args=(datalayer.pk, ))
    response = client.get(url)
    etag = response['ETag']
    url = reverse('datalayer_update',
                  args=(map.pk, datalayer.pk))
    client.login(username=map.owner.username, password="123123")
    name = 'new name'
    post_data['name'] = 'new name'
    response = client.post(url, post_data, follow=True, HTTP_IF_MATCH=etag)
    assert response.status_code == 200
    modified_datalayer = DataLayer.objects.get(pk=datalayer.pk)
    assert modified_datalayer.name == name


def test_optimistic_concurrency_control_with_bad_etag(client, datalayer, map, post_data):  # noqa
    url = reverse('datalayer_update', args=(map.pk, datalayer.pk))
    client.login(username=map.owner.username, password='123123')
    name = 'new name'
    post_data['name'] = name
    response = client.post(url, post_data, follow=True, HTTP_IF_MATCH='xxx')
    assert response.status_code == 412
    modified_datalayer = DataLayer.objects.get(pk=datalayer.pk)
    assert modified_datalayer.name != name


def test_optimistic_concurrency_control_with_empty_etag(client, datalayer, map, post_data):  # noqa
    url = reverse('datalayer_update', args=(map.pk, datalayer.pk))
    client.login(username=map.owner.username, password='123123')
    name = 'new name'
    post_data['name'] = name
    response = client.post(url, post_data, follow=True, HTTP_IF_MATCH=None)
    assert response.status_code == 200
    modified_datalayer = DataLayer.objects.get(pk=datalayer.pk)
    assert modified_datalayer.name == name


def test_versions_should_return_versions(client, datalayer, map, settings):
    root = datalayer.storage_root()
    datalayer.geojson.storage.save(
        '%s/%s_1440924889.geojson' % (root, datalayer.pk),
        ContentFile("{}"))
    datalayer.geojson.storage.save(
        '%s/%s_1440923687.geojson' % (root, datalayer.pk),
        ContentFile("{}"))
    datalayer.geojson.storage.save(
        '%s/%s_1440918637.geojson' % (root, datalayer.pk),
        ContentFile("{}"))
    url = reverse('datalayer_versions', args=(datalayer.pk, ))
    versions = json.loads(client.get(url).content.decode())
    assert len(versions['versions']) == 4
    version = {'name': '%s_1440918637.geojson' % datalayer.pk, 'size': 2,
               'at': '1440918637'}
    assert version in versions['versions']


def test_version_should_return_one_version_geojson(client, datalayer, map):
    root = datalayer.storage_root()
    name = '%s_1440924889.geojson' % datalayer.pk
    datalayer.geojson.storage.save('%s/%s' % (root, name), ContentFile("{}"))
    url = reverse('datalayer_version', args=(datalayer.pk, name))
    assert client.get(url).content.decode() == "{}"
