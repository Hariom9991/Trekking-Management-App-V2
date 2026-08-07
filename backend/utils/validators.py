ALLOWED_TREK_STATUS = {'pending', 'approved', 'open', 'closed', 'completed', 'ongoing'}
ALLOWED_BOOKING_STATUS = {'booked', 'cancelled', 'completed'}
ALLOWED_USER_STATUS = {'active', 'blacklisted'}
ALLOWED_DIFFICULTY = {'Easy', 'Moderate', 'Hard'}


def validate_trek_payload(data):
    errors = []
    if not data.get('trek_name'): errors.append('Trek name is required.')
    if not data.get('location'): errors.append('Location is required.')
    if data.get('difficulty') not in ALLOWED_DIFFICULTY: errors.append('Difficulty must be Easy, Moderate, or Hard.')
    try:
        if int(data.get('duration_days', 0)) < 1: errors.append('Duration must be at least 1 day.')
        if int(data.get('total_slots', 0)) < 1: errors.append('Total slots must be at least 1.')
        if int(data.get('available_slots', -1)) < 0: errors.append('Available slots cannot be negative.')
    except Exception:
        errors.append('Numeric fields are invalid.')
    if data.get('status') not in ALLOWED_TREK_STATUS: errors.append('Invalid trek status.')
    if data.get('start_date') and data.get('end_date') and data.get('end_date') < data.get('start_date'):
        errors.append('End date cannot be before start date.')
    return errors
