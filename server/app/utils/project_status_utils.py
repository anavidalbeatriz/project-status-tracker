"""
Utility functions for project status calculations.
"""

def calculate_project_health_status(status: dict) -> str:
    """
    Calculate the overall project health status based on the three boolean fields.
    
    Args:
        status: Dictionary with is_on_scope, is_on_time, is_on_budget
        
    Returns:
        'green' if 3 are true, 'yellow' if 2 are true, 'red' if 0-1 are true
    """
    if not status:
        return 'red'
    
    green_count = sum([
        1 if status.get('is_on_scope') is True else 0,
        1 if status.get('is_on_time') is True else 0,
        1 if status.get('is_on_budget') is True else 0
    ])
    
    if green_count >= 3:
        return 'green'
    elif green_count == 2:
        return 'yellow'
    else:
        return 'red'


def get_health_status_label(status: str) -> str:
    """Get a human-readable label for the health status."""
    labels = {
        'green': 'Healthy',
        'yellow': 'At Risk',
        'red': 'Critical'
    }
    return labels.get(status, 'Unknown')
