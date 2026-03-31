// Custom JavaScript for Fact Checker Application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Character count for textareas
    initCharacterCount();
    
    // Vote button handlers
    initVoteButtons();
    
    // Comment collapse/expand
    initCommentToggle();
    
    // Auto-dismiss alerts
    initAutoDismissAlerts();
});

/**
 * Initialize character count for textareas with data-max-length attribute
 */
function initCharacterCount() {
    const textareas = document.querySelectorAll('textarea[data-max-length]');
    
    textareas.forEach(textarea => {
        const maxLength = parseInt(textarea.getAttribute('data-max-length'));
        const countElement = document.createElement('div');
        countElement.className = 'character-count';
        textarea.parentNode.appendChild(countElement);
        
        function updateCount() {
            const currentLength = textarea.value.length;
            const remaining = maxLength - currentLength;
            
            countElement.textContent = `${currentLength}/${maxLength}`;
            
            // Update styling based on remaining characters
            countElement.classList.remove('warning', 'danger');
            if (remaining < 50) {
                countElement.classList.add('warning');
            }
            if (remaining < 10) {
                countElement.classList.add('danger');
            }
        }
        
        textarea.addEventListener('input', updateCount);
        updateCount(); // Initial count
    });
}

/**
 * Initialize vote button functionality
 */
function initVoteButtons() {
    // Fact vote buttons
    document.querySelectorAll('.fact-vote-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const factId = this.getAttribute('data-fact-id');
            const voteType = this.getAttribute('data-vote-type');
            
            // Show loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span>';
            this.disabled = true;
            
            // Make AJAX request
            fetch(`/api/voting/fact/${factId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ vote_type: voteType })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update vote counts
                    updateVoteCounts(factId, data.vote_counts);
                    
                    // Update button states
                    updateFactVoteButtons(factId, data.user_vote);
                } else {
                    showAlert('error', data.message || 'Failed to submit vote');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('error', 'An error occurred while submitting your vote');
            })
            .finally(() => {
                // Restore button state
                this.innerHTML = originalText;
                this.disabled = false;
            });
        });
    });
    
    // Comment vote buttons
    document.querySelectorAll('.comment-vote-btn').forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            const commentId = this.getAttribute('data-comment-id');
            const voteType = this.getAttribute('data-vote-type');
            
            // Make AJAX request
            fetch(`/api/voting/comment/${commentId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({ vote_type: voteType })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update vote counts
                    updateCommentVoteCounts(commentId, data.vote_counts);
                    
                    // Update button states
                    updateCommentVoteButtons(commentId, data.user_vote);
                } else {
                    showAlert('error', data.message || 'Failed to submit vote');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showAlert('error', 'An error occurred while submitting your vote');
            });
        });
    });
}

/**
 * Initialize comment collapse/expand functionality
 */
function initCommentToggle() {
    document.querySelectorAll('.comment-toggle').forEach(button => {
        button.addEventListener('click', function() {
            const commentId = this.getAttribute('data-comment-id');
            const repliesContainer = document.querySelector(`#replies-${commentId}`);
            
            if (repliesContainer) {
                if (repliesContainer.style.display === 'none') {
                    repliesContainer.style.display = 'block';
                    this.innerHTML = '<i class="bi bi-dash"></i> Hide Replies';
                } else {
                    repliesContainer.style.display = 'none';
                    this.innerHTML = '<i class="bi bi-plus"></i> Show Replies';
                }
            }
        });
    });
}

/**
 * Initialize auto-dismiss alerts
 */
function initAutoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000); // Auto-dismiss after 5 seconds
    });
}

/**
 * Update fact vote counts in the UI
 */
function updateVoteCounts(factId, voteCounts) {
    const factCountElement = document.querySelector(`#fact-count-${factId}`);
    const fakeCountElement = document.querySelector(`#fake-count-${factId}`);
    
    if (factCountElement) {
        factCountElement.textContent = voteCounts.fact_votes;
    }
    if (fakeCountElement) {
        fakeCountElement.textContent = voteCounts.fake_votes;
    }
}

/**
 * Update fact vote button states
 */
function updateFactVoteButtons(factId, userVote) {
    const factButton = document.querySelector(`[data-fact-id="${factId}"][data-vote-type="fact"]`);
    const fakeButton = document.querySelector(`[data-fact-id="${factId}"][data-vote-type="fake"]`);
    
    // Remove active class from both buttons
    if (factButton) factButton.classList.remove('active');
    if (fakeButton) fakeButton.classList.remove('active');
    
    // Add active class to the voted button
    if (userVote === 'fact' && factButton) {
        factButton.classList.add('active');
    } else if (userVote === 'fake' && fakeButton) {
        fakeButton.classList.add('active');
    }
}

/**
 * Update comment vote counts in the UI
 */
function updateCommentVoteCounts(commentId, voteCounts) {
    const scoreElement = document.querySelector(`#comment-score-${commentId}`);
    
    if (scoreElement) {
        const score = voteCounts.upvotes - voteCounts.downvotes;
        scoreElement.textContent = score;
    }
}

/**
 * Update comment vote button states
 */
function updateCommentVoteButtons(commentId, userVote) {
    const upvoteButton = document.querySelector(`[data-comment-id="${commentId}"][data-vote-type="upvote"]`);
    const downvoteButton = document.querySelector(`[data-comment-id="${commentId}"][data-vote-type="downvote"]`);
    
    // Remove active class from both buttons
    if (upvoteButton) upvoteButton.classList.remove('active');
    if (downvoteButton) downvoteButton.classList.remove('active');
    
    // Add active class to the voted button
    if (userVote === 'upvote' && upvoteButton) {
        upvoteButton.classList.add('active');
    } else if (userVote === 'downvote' && downvoteButton) {
        downvoteButton.classList.add('active');
    }
}

/**
 * Show alert message
 */
function showAlert(type, message) {
    const alertContainer = document.querySelector('.container');
    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.insertBefore(alertElement, alertContainer.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertElement);
        bsAlert.close();
    }, 5000);
}

/**
 * Get CSRF token from meta tag or form
 */
function getCSRFToken() {
    const metaTag = document.querySelector('meta[name="csrf-token"]');
    if (metaTag) {
        return metaTag.getAttribute('content');
    }
    
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    return '';
}

/**
 * Confirm action with user
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Format date for display
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now - date);
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) {
        return 'Yesterday';
    } else if (diffDays < 7) {
        return `${diffDays} days ago`;
    } else {
        return date.toLocaleDateString();
    }
}

/**
 * Debounce function for search inputs
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}
