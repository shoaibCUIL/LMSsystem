"""
UPDATE THIS ROUTE IN app.py

Replace the existing enroll_course route with this version:
"""

@app.route('/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_course(course_id):
    """Enroll user in a course with automatic payment redirect"""
    course = Course.query.get_or_404(course_id)
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(
        user_id=current_user.id,
        course_id=course_id
    ).first()
    
    if existing_enrollment:
        if existing_enrollment.payment_status in ['verified', 'free']:
            flash('You are already enrolled in this course.', 'info')
            return redirect(url_for('course_detail', course_id=course_id))
        elif existing_enrollment.payment_status == 'pending':
            flash('Your enrollment is pending payment verification.', 'warning')
            return redirect(url_for('payment_instructions', course_id=course_id))
    
    # Create new enrollment
    try:
        # Determine payment status
        if course.is_free:
            payment_status = 'free'
            is_active = True
            flash(f'✅ Successfully enrolled in {course.title}!', 'success')
            redirect_url = url_for('dashboard')
        else:
            payment_status = 'pending'
            is_active = False
            # SUCCESS MESSAGE FIRST
            flash(f'✅ Registration Successful for {course.title}!', 'success')
            flash('Please complete payment to activate your course access.', 'info')
            redirect_url = url_for('payment_instructions', course_id=course_id)
        
        enrollment = Enrollment(
            user_id=current_user.id,
            course_id=course_id,
            enrolled_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=course.duration_days),
            payment_status=payment_status,
            is_active=is_active
        )
        db.session.add(enrollment)
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash('An error occurred during enrollment. Please try again.', 'danger')
        app.logger.error(f'Enrollment error: {str(e)}')
        return redirect(url_for('course_detail', course_id=course_id))
    
    # AUTOMATIC REDIRECT
    return redirect(redirect_url)
