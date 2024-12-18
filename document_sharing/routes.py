from flask import Blueprint, request, jsonify
from models import db, User, Document, AccessControl

routes = Blueprint('routes', __name__)

#create a document
@routes.route('/documents', methods=['POST'])
def create_document():
    data = request.json
    owner_email = data.get('owner_email')
    document_name = data.get('name')

    if not owner_email or not document_name:
        return jsonify({"message": "Missing required fields: owner_email, name"}), 400

    user = User.query.filter_by(email=owner_email).first()
    if not user:
        user = User(email=owner_email)
        db.session.add(user)
        db.session.commit()

    document = Document(name=document_name, owner_email=owner_email)
    db.session.add(document)
    db.session.commit()
    return jsonify({"message": "Document created", "document_id": document.id}), 201


#view document
@routes.route('/documents/<int:document_id>', methods=['GET'])
def view_document(document_id):
    document = Document.query.get(document_id)
    if not document:
        return jsonify({"message": "Document not found"}), 404

    #if public
    if document.is_public:
        return jsonify({"document_id": document.id, "name": document.name, "is_public": document.is_public}), 200

    #user access
    user_email = request.args.get('user_email')
    if not user_email:
        return jsonify({"message": "User email is required"}), 400

    if document.owner_email == user_email or AccessControl.query.filter_by(document_id=document_id, user_email=user_email).first():
        return jsonify({"document_id": document.id, "name": document.name, "is_public": document.is_public}), 200

    return jsonify({"message": "Access denied"}), 403


#edit document
@routes.route('/documents/<int:document_id>', methods=['PUT'])
def edit_document(document_id):
    data = request.json
    user_email = data.get('user_email')
    new_name = data.get('name')

    if not user_email or not new_name:
        return jsonify({"message": "Missing required fields: user_email, name"}), 400

    document = Document.query.get(document_id)
    if not document:
        return jsonify({"message": "Document not found"}), 404

    #check  --> for write  access
    access = AccessControl.query.filter_by(document_id=document_id, user_email=user_email).first()
    if document.owner_email != user_email and (not access or access.access_level != 'write'):
        return jsonify({"message": "Access denied"}), 403

    document.name = new_name
    db.session.commit()
    return jsonify({"message": "Document updated"}), 200


#Grant access
@routes.route('/documents/<int:document_id>/access', methods=['POST'])
def grant_access(document_id):
    data = request.json
    user_email = data.get('user_email')
    access_level = data.get('access_level')

    if not user_email or not access_level:
        return jsonify({"message": "Missing required fields: user_email, access_level"}), 400

    if access_level not in ['read', 'write']:
        return jsonify({"message": "Invalid access level"}), 400

    access = AccessControl(document_id=document_id, user_email=user_email, access_level=access_level)
    db.session.add(access)
    db.session.commit()
    return jsonify({"message": f"Access granted to {user_email} with {access_level} rights"}), 201


#edit access
@routes.route('/documents/<int:document_id>/access', methods=['PUT'])
def edit_access(document_id):
    data = request.json
    user_email = data.get('user_email')
    new_access_level = data.get('access_level')

    if not user_email or not new_access_level:
        return jsonify({"message": "Missing required fields: user_email, access_level"}), 400

    if new_access_level not in ['read', 'write']:
        return jsonify({"message": "Invalid access level"}), 400

    access = AccessControl.query.filter_by(document_id=document_id, user_email=user_email).first()
    if not access:
        return jsonify({"message": "Access record not found"}), 404

    access.access_level = new_access_level
    db.session.commit()
    return jsonify({"message": f"Access updated to {new_access_level} for {user_email}"}), 200

#delete doc
@routes.route('/documents/<int:document_id>', methods=['DELETE'])
def delete_document(document_id):

    document = Document.query.get(document_id)
    if not document:
        return jsonify({"message": "Document not found"}), 404

    user_email = request.args.get('user_email') 

    if document.owner_email != user_email:
        return jsonify({"message": "Only the owner can delete the document"}), 403

    #delete access control records related to the document
    AccessControl.query.filter_by(document_id=document_id).delete()

    #delete the document
    db.session.delete(document)
    db.session.commit()

    return jsonify({"message": "Document deleted successfully"}), 200

#toggle public visibility
@routes.route('/documents/<int:document_id>/public', methods=['PUT'])
def make_document_public(document_id):
    data = request.json
    is_public = data.get('is_public', False)
    user_email = data.get('user_email')

    if not user_email:
        return jsonify({"message": "User email is required"}), 400

    document = Document.query.get(document_id)
    if not document:
        return jsonify({"message": "Document not found"}), 404

    if document.owner_email != user_email:
        return jsonify({"message": "Only the owner can change visibility"}), 403

    document.is_public = is_public
    db.session.commit()
    return jsonify({"message": f"Document visibility updated to {'public' if is_public else 'private'}"}), 200


#get all public documents
@routes.route('/documents/public', methods=['GET'])
def get_public_documents():
    public_docs = Document.query.filter_by(is_public=True).all()
    result = [{"id": doc.id, "name": doc.name} for doc in public_docs]
    return jsonify({"public_documents": result}), 200


#get all documents a user has access to created/shared with them
@routes.route('/documents/user_access', methods=['GET'])
def get_user_documents():
    user_email = request.args.get('user_email')

    if not user_email:
        return jsonify({"message": "User email is required"}), 400

    #all documents created by the user(owner)
    owned_documents = Document.query.filter_by(owner_email=user_email).all()

    #all documents created by the user(accessControl) 
    shared_documents = AccessControl.query.filter_by(user_email=user_email).all()
    shared_document_ids = [access.document_id for access in shared_documents]
    shared_documents = Document.query.filter(Document.id.in_(shared_document_ids)).all()

    #combined
    all_documents = owned_documents + shared_documents

    #create response
    result = [{"id": doc.id, "name": doc.name, "is_public": doc.is_public} for doc in all_documents]
    return jsonify({"documents": result}), 200
