import time

from flask import Blueprint, jsonify, render_template, request, session
from models.retirement_account import RetirementAccount
from models.user import User
from extensions import db
import logging

retirement_bp = Blueprint("retirement", __name__, url_prefix="/apps/401k")

@retirement_bp.route("/")
def retirement_dashboard():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401
    return render_template("401k.html", username=session["user"])


@retirement_bp.route("/balance")
def get_balance():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    username = session["user"]
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    account = RetirementAccount.query.filter_by(user_id=user.id).first()
    
    # Create account if it doesn't exist
    if not account:
        account = RetirementAccount(user_id=user.id)
        db.session.add(account)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to create account: {str(e)}")
            return jsonify({"error": "Failed to create account"}), 500
        
    return jsonify(account.to_dict())


@retirement_bp.route("/contribute", methods=["POST"])
def contribute():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    data = request.get_json()
    amount = data.get("amount", 0)

    username = session["user"]
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    account = RetirementAccount.query.filter_by(user_id=user.id).first()
    
    # Create account if it doesn't exist
    if not account:
        account = RetirementAccount(user_id=user.id)
        db.session.add(account)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logging.error(f"Failed to create account: {str(e)}")
            return jsonify({"error": "Failed to create account"}), 500
    
    if amount <= 0:
        return jsonify({
            "message": "Invalid contribution amount!",
            "funds": account.funds,
            "401k_balance": account.retirement_balance
        }), 400

    if amount > account.funds:
        return jsonify({
            "message": "Insufficient personal funds for this contribution!",
            "funds": account.funds, 
            "401k_balance": account.retirement_balance
        }), 400

    # Implementing atomic transaction with db.session to prevent race conditions
    try:
        company_match = amount * 0.5
        total_contribution = amount + company_match

        account.funds -= amount  # Deduct funds
        account.retirement_balance += total_contribution  # Add to 401k balance
        
        db.session.commit()
        
        return jsonify({
            "message": f"Contributed ${amount}. Employer matched ${company_match}!",
            "funds": account.funds,
            "401k_balance": account.retirement_balance
        })
    except Exception as e:
        db.session.rollback()
        logging.error(f"Transaction failed: {str(e)}")
        return jsonify({"error": "Transaction failed"}), 500


@retirement_bp.route("/reset", methods=["POST"])
def reset_account():
    if "user" not in session:
        return jsonify({"error": "Not logged in"}), 401

    username = session["user"]
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"error": "User not found"}), 404
        
    account = RetirementAccount.query.filter_by(user_id=user.id).first()
    
    if not account:
        account = RetirementAccount(user_id=user.id)
        db.session.add(account)
    else:
        account.funds = 10000
        account.retirement_balance = 0
        
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logging.error(f"Failed to reset account: {str(e)}")
        return jsonify({"error": "Failed to reset account"}), 500

    return jsonify({
        "message": "Account reset successfully!",
        "funds": account.funds,
        "401k_balance": account.retirement_balance
    })
