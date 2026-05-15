import firebase_admin
from firebase_admin import credentials, firestore
import os
from datetime import datetime

# Initialize Firebase
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate('firebase-key.json')
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print(f"Firebase Init Error: {e}")

db = firestore.client()

# ============================
# USERS
# ============================
def get_user_by_id(user_id):
    doc = db.collection('users').document(str(user_id)).get()
    if doc.exists:
        data = doc.to_dict()
        data['id'] = doc.id
        return data
    return None

def get_user_by_email(email):
    docs = db.collection('users').where('email', '==', email).limit(1).stream()
    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        return data
    return None

def get_user_by_username(username):
    docs = db.collection('users').where('username', '==', username).limit(1).stream()
    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        return data
    return None

def get_admins():
    docs = db.collection('users').where('role', '==', 'admin').stream()
    admins = []
    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        admins.append(data)
    return admins

def create_user(username, email, password_hash, role, department=None):
    doc_ref = db.collection('users').document()
    doc_ref.set({
        'username': username,
        'email': email,
        'password': password_hash,
        'role': role,
        'department': department,
        'created_at': datetime.utcnow()
    })
    return doc_ref.id

# ============================
# TICKETS
# ============================
def get_all_tickets():
    docs = db.collection('tickets').order_by('created_at', direction=firestore.Query.DESCENDING).stream()
    tickets = []
    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        # Fetch user
        user = get_user_by_id(data.get('user_id'))
        if user:
            data['username'] = user.get('username')
            data['email'] = user.get('email')
        tickets.append(data)
    return tickets

def get_tickets_by_user(user_id):
    docs = db.collection('tickets').where('user_id', '==', str(user_id)).order_by('created_at', direction=firestore.Query.DESCENDING).stream()
    tickets = []
    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        tickets.append(data)
    return tickets

def get_ticket_by_id(ticket_id):
    doc = db.collection('tickets').document(str(ticket_id)).get()
    if doc.exists:
        data = doc.to_dict()
        data['id'] = doc.id
        user = get_user_by_id(data.get('user_id'))
        if user:
            data['username'] = user.get('username')
            data['email'] = user.get('email')
        return data
    return None

def create_ticket(ticket_text, category, tone, response, user_id, assigned_to=None, status='Open', priority_level='Normal', requires_approval=0, is_approved=0, risk_level='Low', bias_flag='No', attachment_path=None):
    doc_ref = db.collection('tickets').document()
    doc_ref.set({
        'ticket_text': ticket_text,
        'category': category,
        'tone': tone,
        'response': response,
        'user_id': str(user_id),
        'assigned_to': str(assigned_to) if assigned_to else None,
        'status': status,
        'priority_level': priority_level,
        'requires_approval': requires_approval,
        'is_approved': is_approved,
        'risk_level': risk_level,
        'bias_flag': bias_flag,
        'attachment_path': attachment_path,
        'created_at': datetime.utcnow()
    })
    return doc_ref.id

def update_ticket(ticket_id, updates):
    doc_ref = db.collection('tickets').document(str(ticket_id))
    doc_ref.update(updates)

def delete_ticket(ticket_id):
    db.collection('tickets').document(str(ticket_id)).delete()

# ============================
# NOTIFICATIONS & AUDIT LOGS
# ============================
def create_notification(user_id, message, type="Update"):
    doc_ref = db.collection('notifications').document()
    doc_ref.set({
        'user_id': str(user_id),
        'message': message,
        'type': type,
        'is_read': 0,
        'created_at': datetime.utcnow()
    })
    return doc_ref.id

def log_action(action, table_name, row_id, old_value, new_value, performer):
    doc_ref = db.collection('audit_log').document()
    doc_ref.set({
        'action': action,
        'table_name': table_name,
        'row_id': str(row_id),
        'old_value': str(old_value) if old_value else None,
        'new_value': str(new_value) if new_value else None,
        'performer': performer,
        'timestamp': datetime.utcnow()
    })
    return doc_ref.id
