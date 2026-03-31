"""
Voting routes for AJAX voting functionality.
"""
from flask import Blueprint, request, jsonify, abort
from app.components.auth.services import SessionValidationService
from app.components.voting.services import VotingService, VoteFraudDetectionService

voting_bp = Blueprint('voting', __name__, url_prefix='/api/voting')


@voting_bp.route('/fact/<fact_id>', methods=['POST'])
@SessionValidationService.require_authentication()
def vote_fact(fact_id):
    """Cast a vote on a fact via AJAX."""
    user = SessionValidationService.get_current_user()
    
    try:
        data = request.get_json()
        if not data or 'vote_type' not in data:
            return jsonify({'success': False, 'message': 'Vote type required'}), 400
        
        vote_type = data['vote_type']
        
        # Check for fraud
        should_block, block_reason = VoteFraudDetectionService.should_block_vote(user.id)
        if should_block:
            return jsonify({
                'success': False, 
                'message': f'Vote blocked: {block_reason}'
            }), 429
        
        # Cast vote
        success, message, vote_counts = VotingService.vote_on_fact(user.id, fact_id, vote_type)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'vote_counts': vote_counts,
                'user_vote': vote_type
            })
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'Voting failed'}), 500


@voting_bp.route('/fact/<fact_id>', methods=['DELETE'])
@SessionValidationService.require_authentication()
def remove_fact_vote(fact_id):
    """Remove a vote from a fact via AJAX."""
    user = SessionValidationService.get_current_user()
    
    try:
        success, message, vote_counts = VotingService.remove_fact_vote(user.id, fact_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'vote_counts': vote_counts,
                'user_vote': None
            })
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'Vote removal failed'}), 500


@voting_bp.route('/comment/<comment_id>', methods=['POST'])
@SessionValidationService.require_authentication()
def vote_comment(comment_id):
    """Cast a vote on a comment via AJAX."""
    user = SessionValidationService.get_current_user()
    
    try:
        data = request.get_json()
        if not data or 'vote_type' not in data:
            return jsonify({'success': False, 'message': 'Vote type required'}), 400
        
        vote_type = data['vote_type']
        
        # Check for fraud
        should_block, block_reason = VoteFraudDetectionService.should_block_vote(user.id)
        if should_block:
            return jsonify({
                'success': False, 
                'message': f'Vote blocked: {block_reason}'
            }), 429
        
        # Cast vote
        success, message, vote_counts = VotingService.vote_on_comment(user.id, comment_id, vote_type)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'vote_counts': vote_counts,
                'user_vote': vote_type
            })
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'Voting failed'}), 500


@voting_bp.route('/comment/<comment_id>', methods=['DELETE'])
@SessionValidationService.require_authentication()
def remove_comment_vote(comment_id):
    """Remove a vote from a comment via AJAX."""
    user = SessionValidationService.get_current_user()
    
    try:
        success, message, vote_counts = VotingService.remove_comment_vote(user.id, comment_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'vote_counts': vote_counts,
                'user_vote': None
            })
        else:
            return jsonify({'success': False, 'message': message}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': 'Vote removal failed'}), 500


@voting_bp.route('/fact/<fact_id>/counts', methods=['GET'])
def get_fact_vote_counts(fact_id):
    """Get current vote counts for a fact."""
    try:
        vote_counts = VotingService.get_fact_vote_counts(fact_id)
        
        # Get user's current vote if authenticated
        user_vote = None
        user = SessionValidationService.get_current_user()
        if user:
            user_vote = VotingService.get_user_vote_on_fact(user.id, fact_id)
        
        return jsonify({
            'success': True,
            'vote_counts': vote_counts,
            'user_vote': user_vote
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to get vote counts'}), 500


@voting_bp.route('/comment/<comment_id>/counts', methods=['GET'])
def get_comment_vote_counts(comment_id):
    """Get current vote counts for a comment."""
    try:
        vote_counts = VotingService.get_comment_vote_counts(comment_id)
        
        # Get user's current vote if authenticated
        user_vote = None
        user = SessionValidationService.get_current_user()
        if user:
            user_vote = VotingService.get_user_vote_on_comment(user.id, comment_id)
        
        return jsonify({
            'success': True,
            'vote_counts': vote_counts,
            'user_vote': user_vote
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to get vote counts'}), 500


@voting_bp.route('/fraud-check/<user_id>', methods=['GET'])
@SessionValidationService.require_admin()
def fraud_check(user_id):
    """Admin endpoint to check for voting fraud."""
    try:
        hours = request.args.get('hours', 24, type=int)
        fraud_results = VoteFraudDetectionService.detect_suspicious_voting_patterns(user_id, hours)
        
        return jsonify({
            'success': True,
            'fraud_results': fraud_results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': 'Fraud check failed'}), 500
