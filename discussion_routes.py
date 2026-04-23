from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from database import db
from models import Course, DiscussionRoom, DiscussionSession, DiscussionSubscription, DiscussionMessage
from utils import save_receipt

discussion_bp = Blueprint('discussion', __name__, url_prefix='/discussion')


def get_price_per_hour(topic):
    """
    Dynamic pricing based on topic complexity.
    Admin can extend this logic freely.
    """
    topic_lower = topic.lower()
    if any(w in topic_lower for w in ['advanced', 'computational', 'nlp', 'machine', 'research']):
        return 500   # Advanced topic
    elif any(w in topic_lower for w in ['corpus', 'intermediate', 'analysis', 'syntax']):
        return 350   # Intermediate topic
    else:
        return 250   # Beginner/general topic


@discussion_bp.route('/')
def rooms():
    """List all active discussion rooms"""
    all_rooms = DiscussionRoom.query.filter_by(is_active=True).all()
    return render_template('discussion/rooms.html', rooms=all_rooms)


@discussion_bp.route('/room/<int:room_id>')
@login_required
def room(room_id):
    """Main discussion room — chat + upcoming sessions"""
    discussion_room = DiscussionRoom.query.get_or_404(room_id)

    # Check subscription
    subscription = DiscussionSubscription.query.filter_by(
        user_id=current_user.id,
        room_id=room_id
    ).filter(DiscussionSubscription.status == 'approved').first()

    has_access = (subscription and subscription.is_active()) or current_user.is_admin

    # Upcoming + live sessions
    upcoming_sessions = DiscussionSession.query.filter_by(
        room_id=room_id, is_active=True
    ).filter(
        DiscussionSession.scheduled_at >= datetime.utcnow()
    ).order_by(DiscussionSession.scheduled_at).limit(5).all()

    live_session = None
    for s in DiscussionSession.query.filter_by(room_id=room_id, is_active=True).all():
        if s.is_live():
            live_session = s
            break

    # Chat messages (last 50)
    messages = DiscussionMessage.query.filter_by(
        room_id=room_id, is_deleted=False
    ).order_by(DiscussionMessage.created_at.desc()).limit(50).all()
    messages = list(reversed(messages))

    return render_template('discussion/room.html',
                           room=discussion_room,
                           has_access=has_access,
                           subscription=subscription,
                           upcoming_sessions=upcoming_sessions,
                           live_session=live_session,
                           messages=messages)


@discussion_bp.route('/room/<int:room_id>/send', methods=['POST'])
@login_required
def send_message(room_id):
    """Send a chat message — AJAX endpoint"""
    discussion_room = DiscussionRoom.query.get_or_404(room_id)

    # Verify access
    subscription = DiscussionSubscription.query.filter_by(
        user_id=current_user.id,
        room_id=room_id,
        status='approved'
    ).first()

    if not ((subscription and subscription.is_active()) or current_user.is_admin):
        return jsonify({'error': 'No active subscription'}), 403

    content = request.json.get('content', '').strip()
    if not content or len(content) > 1000:
        return jsonify({'error': 'Invalid message'}), 400

    msg = DiscussionMessage(
        room_id=room_id,
        user_id=current_user.id,
        content=content
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({
        'id': msg.id,
        'content': msg.content,
        'user': f'{current_user.first_name} {current_user.last_name}',
        'is_admin': current_user.is_admin,
        'time': msg.created_at.strftime('%I:%M %p')
    })


@discussion_bp.route('/room/<int:room_id>/messages')
@login_required
def get_messages(room_id):
    """Poll for new messages — AJAX endpoint"""
    after_id = request.args.get('after', 0, type=int)

    subscription = DiscussionSubscription.query.filter_by(
        user_id=current_user.id,
        room_id=room_id,
        status='approved'
    ).first()

    if not ((subscription and subscription.is_active()) or current_user.is_admin):
        return jsonify({'error': 'No access'}), 403

    messages = DiscussionMessage.query.filter(
        DiscussionMessage.room_id == room_id,
        DiscussionMessage.id > after_id,
        DiscussionMessage.is_deleted == False
    ).order_by(DiscussionMessage.created_at).limit(30).all()

    return jsonify([{
        'id': m.id,
        'content': m.content,
        'user': f'{m.user.first_name} {m.user.last_name}',
        'is_admin': m.user.is_admin,
        'time': m.created_at.strftime('%I:%M %p')
    } for m in messages])


@discussion_bp.route('/room/<int:room_id>/subscribe', methods=['GET', 'POST'])
@login_required
def subscribe(room_id):
    """Subscribe to a discussion room with flexible pricing"""
    discussion_room = DiscussionRoom.query.get_or_404(room_id)

    # Already has active subscription?
    existing = DiscussionSubscription.query.filter_by(
        user_id=current_user.id,
        room_id=room_id
    ).filter(DiscussionSubscription.status.in_(['pending', 'approved'])).first()

    if existing:
        flash('You already have an active or pending subscription for this room.', 'info')
        return redirect(url_for('discussion.room', room_id=room_id))

    if request.method == 'POST':
        try:
            topic = request.form.get('topic', '').strip()
            duration_days = int(request.form.get('duration_days', 30))
            hours_per_day = int(request.form.get('hours_per_day', 1))
            payment_method = request.form.get('payment_method', '')

            if not topic or not payment_method:
                flash('Please fill all fields.', 'danger')
                return redirect(request.url)

            # Dynamic pricing
            price_per_hour = get_price_per_hour(topic)
            total_hours = duration_days * hours_per_day
            total_price = price_per_hour * total_hours

            # International users pay double
            if current_user.country != 'Pakistan':
                total_price *= 2

            # Save receipt
            receipt_file = request.files.get('payment_receipt')
            if not receipt_file or receipt_file.filename == '':
                flash('Please upload a payment receipt.', 'danger')
                return redirect(request.url)

            receipt_filename = save_receipt(receipt_file)
            if not receipt_filename:
                flash('Failed to upload receipt.', 'danger')
                return redirect(request.url)

            sub = DiscussionSubscription(
                user_id=current_user.id,
                room_id=room_id,
                topic=topic,
                duration_days=duration_days,
                hours_per_day=hours_per_day,
                total_hours=total_hours,
                price_per_hour=price_per_hour,
                total_price=total_price,
                payment_method=payment_method,
                payment_receipt=receipt_filename,
                status='pending'
            )
            db.session.add(sub)
            db.session.commit()

            flash('Subscription submitted! Awaiting admin approval.', 'success')
            return redirect(url_for('discussion.room', room_id=room_id))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Discussion subscription error: {str(e)}')
            flash('An error occurred. Please try again.', 'danger')

    return render_template('discussion/subscribe.html',
                           room=discussion_room,
                           user=current_user,
                           payment_info=current_app.config['PAYMENT_INFO'])