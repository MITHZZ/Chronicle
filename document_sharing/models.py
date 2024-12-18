from flask_sqlalchemy import SQLAlchemy

import os

if os.path.exists('./instance/document_sharing.db'):
    os.remove('./instance/document_sharing.db')
    print("Old database deleted.")

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, unique=True)

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    owner_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
    is_public = db.Column(db.Boolean, default=False)

class AccessControl(db.Model):
    __tablename__ = 'access_control'
    id = db.Column(db.Integer, primary_key=True,)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    user_email = db.Column(db.String(120), db.ForeignKey('users.email'), nullable=False)
    access_level = db.Column(db.String(10), nullable=False)

# #testing
# from flask import Flask
# app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///document_sharing.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# db.init_app(app)
# with app.app_context():
#     db.create_all()


# with app.app_context():
#     # Add a user
#     new_user = User(email='test@example.com')
#     db.session.add(new_user)
#     db.session.commit()

#     # Add a document
#     new_document = Document(name='Sample Document', owner_email='test@example.com')
#     db.session.add(new_document)
#     db.session.commit()

#     # Add access control for the document
#     new_access = AccessControl(document_id=new_document.id, user_email='test@example.com', access_level='read')
#     db.session.add(new_access)
#     db.session.commit()