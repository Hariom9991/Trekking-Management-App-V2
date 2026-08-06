from models.booking import Booking
from models.trek import Trek


def build_monthly_html():
    total_treks = Trek.query.count()
    conducted = Trek.query.filter(Trek.status.in_(['completed', 'ongoing'])).count()
    participants = Booking.query.filter(Booking.status.in_(['booked', 'completed'])).count()

    trek_counts = {}
    for booking in Booking.query.all():
        if booking.trek:
            trek_counts[booking.trek.trek_name] = trek_counts.get(booking.trek.trek_name, 0) + 1

    popular = sorted(trek_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    rows = ''.join(
        [f'<tr><td>{name}</td><td>{count}</td></tr>' for name, count in popular]
    ) or '<tr><td colspan="2">No data</td></tr>'

    return f'''
    <html><body style="font-family:Arial,sans-serif;padding:24px;">
    <h2>Monthly Trekking Activity Report</h2>
    <p>Total Treks: <strong>{total_treks}</strong></p>
    <p>Treks Conducted/Ongoing: <strong>{conducted}</strong></p>
    <p>Total Participants: <strong>{participants}</strong></p>
    <table border="1" cellpadding="8" cellspacing="0">
    <thead><tr><th>Popular Trek</th><th>Bookings</th></tr></thead><tbody>{rows}</tbody></table>
    </body></html>
    '''