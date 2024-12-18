
Recorder link for this  : https://drive.google.com/drive/folders/1HJ5bNDtWw7w3FIoFFoW0flvpT5D8dgfP?usp=drive_link


Document Sharing 

PS : Implement a sharing mechanism for documents. The output can be a simple backend application with no UI


Feature Flow:

A user can create one or many documents -> Called owner 
A owner has full access to document -> read, write, share, edit access, delete
The email id to which share (read /write ) is given -> shared user

API need to be created :
Create Document - Document has only name as its data
View Document - Fetches the name of the document
Edit Document - Overrides the name of the document
Give Access to the Document - share user
Edit Access to the Document - share user 
Delete the Document - user only owner 

Get all documents a user has access to created/shared with them
Toggle public visibility
Get all public documents



Approach : 

Data Model needed for this applications : 
Document Model - Document id , name , owner email and public flag
Access Control Model - All the documents for which are shared with annother user
User Model  - All the owner user list



