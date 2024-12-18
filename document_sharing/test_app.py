import pytest
from flask import Flask
from models import db, User, Document, AccessControl
from routes import routes  

#configure the test app
@pytest.fixture
def app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True

    db.init_app(app)
    app.register_blueprint(routes)

    with app.app_context():
        db.create_all()
        user = User(email='mithun@mail.com') #data for testing
        db.session.add(user)
        db.session.commit()
    yield app

    #cleanup the db
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

#test
#document creation
def test_create_document(client):
    response = client.post('/documents', json={
        'owner_email': 'mithun@mail.com',
        'name': 'document_1'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == "Document created"
    assert 'document_id' in data

#viewing a document
def test_view_document(client):

    response = client.post('/documents', json={
        'owner_email': 'mithun@mail.com',
        'name': 'document_1'
    })
    document_id = response.get_json()['document_id']

    response = client.get(f'/documents/{document_id}', query_string={'user_email': 'mithun@mail.com'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'document_1'

#view not found
def test_view_document_not_found(client):
    response = client.get('/documents/999')  # Non-existent document ID
    assert response.status_code == 404
    data = response.get_json()
    assert data['message'] == "Document not found"

# invalid access level
def test_invalid_access_level(client):
    response = client.post('/documents', json={
        'owner_email': 'mithun@mail.com',
        'name': 'document_1'
    })
    document_id = response.get_json()['document_id']

    # grant invalid access level
    response = client.post(f'/documents/{document_id}/access', json={
        'user_email': 'mithun2@example.com',
        'access_level': 'invalid'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['message'] == "Invalid access level"

#editing a document
def test_edit_document(client):
    response = client.post('/documents', json={
        'owner_email': 'mithun@mail.com',
        'name': 'document_1'
    })
    document_id = response.get_json()['document_id']

    response = client.put(f'/documents/{document_id}', json={
        'user_email': 'mithun@mail.com',
        'name': 'new_document_1'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "Document updated"

#edit the document as a different user
def test_edit_document_access_denied(client):

    response = client.post('/documents', json={
        'owner_email': 'mithun@mail.com',
        'name': 'new_document_1'
    })
    document_id = response.get_json()['document_id']

    
    response = client.put(f'/documents/{document_id}', json={
        'user_email': 'mithun2@mail.com',
        'name': 'unauthorized'
    })
    assert response.status_code == 403
    data = response.get_json()
    assert data['message'] == "Access denied"

#granting access to another user
def test_grant_access(client):
    response = client.post('/documents', json={
        'owner_email': 'mithun@mail.com',
        'name': 'document_1'
    })
    document_id = response.get_json()['document_id']

    response = client.post(f'/documents/{document_id}/access', json={
        'user_email': 'mithun2@mail.com',
        'access_level': 'read'
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == "Access granted to mithun2@mail.com with read rights"

#public visibility toggle
def test_toggle_public_visibility(client):
    response = client.post('/documents', json={
        'owner_email': 'mithun@mail.com',
        'name': 'Private Document'
    })
    document_id = response.get_json()['document_id']

    response = client.put(f'/documents/{document_id}/public', json={
        'user_email': 'mithun@mail.com',
        'is_public': True
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "Document visibility updated to public"

#getting all public documents
def test_get_public_documents(client):
    response = client.post('/documents', json={
        'owner_email': 'mithun@mail.com',
        'name': 'document_1'
    })
    document_id = response.get_json()['document_id']
    client.put(f'/documents/{document_id}/public', json={
        'user_email': 'mithun@mail.com',
        'is_public': True
    })

    response = client.get('/documents/public')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['public_documents']) > 0
    assert data['public_documents'][0]['name'] == 'document_1'

#getting user-accessible documents
def test_get_user_documents(client):

    client.post('/documents', json={
        'owner_email': 'mithun@mail.com',
        'name': 'owned_document'
    })

    # share another document with the user !
    response = client.post('/documents', json={
        'owner_email': 'mithun2@mail.com',
        'name': 'shared_document'
    })
    document_id = response.get_json()['document_id']
    client.post(f'/documents/{document_id}/access', json={
        'user_email': 'mithun@mail.com',
        'access_level': 'read'
    })

    # fetch user-accessible documents
    response = client.get('/documents/user_access', query_string={'user_email': 'mithun@mail.com'})
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['documents']) == 2
