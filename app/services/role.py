from app.models.role import Role, db
from app.utils.logger import logger
from datetime import datetime
import uuid


# ----------------------------
# CREATE ROLE
# ----------------------------
def create_role(data):
    try:
        role_name = data.get("role_name", "").strip().lower()

        if not role_name:
            return {"error": "role_name is required"}, 400

        existing = Role.query.filter_by(role_name=role_name).first()
        if existing:
            return {"error": "Role already exists"}, 400

        new_role = Role(
            id=str(uuid.uuid4()),
            role_name=role_name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.session.add(new_role)
        db.session.commit()

        logger.info(f"Role created successfully: {role_name}")
        return {
            "status": True,
            "message": "Role created successfully",
            "role": {"id": new_role.id, "role_name": new_role.role_name},
        }, 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating role: {str(e)}")
        return {"error": "Internal server error"}, 500


# ----------------------------
# GET ALL ROLES
# ----------------------------
def get_all_roles():
    try:
        roles = Role.query.all()
        return [
            {
                "id": role.id,
                "role_name": role.role_name,
                "created_at": role.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": role.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for role in roles
        ], 200
    except Exception as e:
        logger.error(f"Error fetching roles: {str(e)}")
        return {"error": "Internal server error"}, 500


# ----------------------------
# GET ROLE BY ID
# ----------------------------
def get_role_by_id(role_id):
    try:
        role = Role.query.get(role_id)
        if not role:
            return {"error": "Role not found"}, 404

        return {
            "id": role.id,
            "role_name": role.role_name,
            "created_at": role.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": role.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }, 200
    except Exception as e:
        logger.error(f"Error fetching role {role_id}: {str(e)}")
        return {"error": "Internal server error"}, 500


# ----------------------------
# UPDATE ROLE
# ----------------------------
def update_role(role_id, data):
    try:
        role = Role.query.get(role_id)
        if not role:
            return {"error": "Role not found"}, 404

        role_name = data.get("role_name")
        if role_name:
            role.role_name = role_name.strip().lower()
        role.updated_at = datetime.utcnow()

        db.session.commit()
        logger.info(f"Role updated successfully: {role.role_name}")
        return {
            "status": True,
            "message": "Role updated successfully",
            "role": {"id": role.id, "role_name": role.role_name},
        }, 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating role {role_id}: {str(e)}")
        return {"error": "Internal server error"}, 500


# ----------------------------
# DELETE ROLE
# ----------------------------
def delete_role(role_id):
    try:
        role = Role.query.get(role_id)
        if not role:
            return {"error": "Role not found"}, 404

        db.session.delete(role)
        db.session.commit()
        logger.info(f"Role deleted successfully: {role.role_name}")
        return {"status": True, "message": "Role deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting role {role_id}: {str(e)}")
        return {"error": "Internal server error"}, 500
