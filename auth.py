from flask import Blueprint, render_template, request, flash, redirect, url_for
from website.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/login/<user_type>', methods=['GET', 'POST'])
def login(user_type):
    if request.method == 'POST':
        p_username = request.form.get('p_username')
        password = request.form.get('password')
        
        user = User.query.filter_by(p_username=p_username, user_type=user_type).first()

        if user:
            if user.flagged:
                flash('Your account has been flagged by the admin and you cannot login.', category='error')
            elif check_password_hash(user.password, password):
                login_user(user, remember=True)
                return redirect(url_for('views.dashboard'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Username does not exist.', category='error')
    return render_template(f'{user_type}_login.html')



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))

@auth.route('/sign-up/<user_type>', methods=['GET', 'POST'])
def sign_up(user_type):
    if request.method == 'POST':
        p_name = request.form.get('p_name')
        email = request.form.get('p_email')
        p_category = request.form.get('p_category')
        p_count = request.form.get('p_count')
        p_bio = request.form.get('p_bio')
        p_username = request.form.get('p_username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        if user_type == "influencer":
            p_niche = request.form.get('p_niche')
            p_platform =  request.form.get('p_platform')
        
        if user_type == "sponsor":
            user = User.query.filter_by(email=email, user_type=user_type).first()
        elif user_type == "influencer":
            user = User.query.filter_by(email=email, user_type=user_type).first()
        else:
            flash('Invalid user type.', category='error')
            return redirect(url_for('auth.sign_up', user_type=user_type))

        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(p_name) < 3:
            flash('Name must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 3:
            flash('Password must be at least 3 characters.', category='error')
        else:
            new_user = User(
                    email=email,
                    p_name=p_name,
                    password=generate_password_hash(password1, method='pbkdf2:sha256'),
                    user_type=user_type,
                    p_category=p_category,
                    p_count=p_count,
                    p_bio=p_bio,
                    p_username=p_username
                )
            db.session.add(new_user)
            db.session.commit()
            if user_type == "influencer":
                user_id = new_user.id
                new_influencer = Influencer(
                    name=p_name,
                    email=email,
                    category=p_category,
                    niche=p_niche,
                    reach=p_count,
                    user_id=user_id,  # Link to the user
                    platform=p_platform,
                    bio=p_bio
                )
                db.session.add(new_influencer)
                db.session.commit()
            
            login_user(new_user, remember=True)
            print(f"User id:{email}, password: {password1} is created!")
            return redirect(url_for('views.dashboard'))
    
    return render_template(f'{user_type}_sign_up.html')


@auth.route('/select-login-type')
def select_login_type():
    return render_template('select_login_type.html')

@auth.route('/select-signup-type')
def select_signup_type():
    return render_template('select_signup_type.html')

@auth.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    user = User.query.get(current_user.id)
    
    if request.method == 'POST':
        user.p_name = request.form.get('p_name')
        user.email = request.form.get('email')
        user.p_category = request.form.get('p_category')
        user.p_count = request.form.get('p_count')
        user.p_bio = request.form.get('p_bio')
        
        try:
            db.session.commit()
            flash('Profile updated successfully!', category='success')
        except:
            db.session.rollback()
            flash('Error updating profile. Please try again.', category='danger')
    
    return redirect(url_for('views.dashboard'))



@auth.route('/create_campaign', methods=['GET', 'POST'])
@login_required
def create_campaign():
    if request.method == 'POST':
        campaign_name = request.form.get('campaign_name')
        description = request.form.get('description')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        budget = request.form.get('budget')
        visibility = request.form.get('visibility')
        goals = request.form.get('goals')
        niche = request.form.get('niche')

        # Validation checks
        if not campaign_name or not description or not start_date or not end_date or not budget:
            flash('All required fields must be filled out.', category='danger')
            return redirect(url_for('auth.create_campaign'))

        # Check if end date is after start date
        if end_date < start_date:
            flash('End date must be after the start date.', category='danger')
            return redirect(url_for('auth.create_campaign'))

        # Convert budget to a float
        try:
            budget = float(budget)
        except ValueError:
            flash('Budget must be a number.', category='danger')
            return redirect(url_for('auth.create_campaign'))

        new_campaign = Campaign(
            name=campaign_name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            visibility=visibility,
            goals=goals,
            niche=niche,
            user_id=current_user.id
        )
        
        try:
            db.session.add(new_campaign)
            db.session.commit()
            flash('Campaign created successfully!', category='success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating campaign: {str(e)}', category='danger')
        
        return redirect(url_for('views.dashboard'))
    
    return render_template('create_campaign.html')

@auth.route('/campaign')
@login_required
def my_campaigns():
    campaigns = Campaign.query.filter_by(user_id=current_user.id).all()
    return render_template('my_campaigns.html', campaigns=campaigns)



@auth.route('/campaign/<int:campaign_id>/update', methods=['GET', 'POST'])
@login_required
def update_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    
    if campaign.user_id != current_user.id:
        flash('Unauthorized action.', category='danger')
        return redirect(url_for('my_campaigns'))
    
    campaign.name = request.form.get('campaign_name')
    campaign.description = request.form.get('description')
    campaign.start_date = request.form.get('start_date')
    campaign.end_date = request.form.get('end_date')
    campaign.budget = request.form.get('budget')
    
    try:
        db.session.commit()
        flash('Campaign updated successfully!', category='success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating campaign: {str(e)}', category='danger')
    
    return redirect(url_for('auth.my_campaigns'))

@auth.route('/campaign/<int:campaign_id>/delete', methods=['POST'])
@login_required
def delete_campaign(campaign_id):
    campaign = Campaign.query.get(campaign_id)
    
    if campaign.user_id != current_user.id:
        flash('Unauthorized action.', category='danger')
        return redirect(url_for('auth.my_campaigns'))
    
    try:
        db.session.delete(campaign)
        db.session.commit()
        flash('Campaign deleted successfully!', category='success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting campaign: {str(e)}', category='danger')
    
    return redirect(url_for('auth.my_campaigns'))

@auth.route('/delete_request/<int:request_id>', methods=['POST'])
@login_required
def delete_request(request_id):
    # Assuming that sponsor_id is the current user's id and you have access to campaign_id
    ad_request = AdRequest.query.join(Campaign).filter(
        AdRequest.id == request_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if ad_request is None:
        flash('Request not found or you do not have permission to delete this request.', 'danger')
        return redirect(url_for('auth.my_campaigns'))
    
    try:
        db.session.delete(ad_request)
        db.session.commit()
        flash('Ad request deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting request: {str(e)}', 'danger')
    
    return redirect(url_for('auth.my_campaigns'))

@auth.route('/update_request/<int:request_id>', methods=['POST'])
@login_required
def update_request(request_id):
    # Query AdRequest with join to Campaign to ensure the user is authorized
    ad_request = AdRequest.query.join(Campaign).filter(
        AdRequest.id == request_id,
        Campaign.user_id == current_user.id
    ).first()
    
    if ad_request is None:
        flash('Request not found or you do not have permission to update this request.', 'danger')
        return redirect(url_for('auth.my_campaigns'))

    try:
        # Update the ad request fields with data from the form
        ad_request.payment_amount = request.form['payment_amount']
        ad_request.requirements = request.form['requirements']
        ad_request.message = request.form['message']

        db.session.commit()
        flash('Ad request updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating request: {str(e)}', 'danger')
    
    return redirect(url_for('auth.my_campaigns'))

@auth.route('/search-influencers', methods=['GET', 'POST'])
@login_required
def search_influencers():
    name = request.args.get('name')
    category = request.args.get('category')
    show_all = request.args.get('show_all')
    campaigns = Campaign.query.filter_by(user_id=current_user.id).all()

    if show_all:
        influencers = Influencer.query.all()
    else:
        query = Influencer.query
        if name:
            query = query.filter(Influencer.name.ilike(f'%{name}%'))
        if category:
            query = query.filter(Influencer.category.ilike(f'%{category}%'))
        influencers = query.all()

    return render_template('search_influencers.html', influencers=influencers,campaigns=campaigns)

@auth.route('/update_influencer_profile', methods=['GET', 'POST'])
@login_required
def update_influencer_profile():
    influencer = Influencer.query.filter_by(user_id=current_user.id).first()
    
    if request.method == 'POST':
        # Update influencer details from the form
        influencer.name = request.form['name']
        influencer.email = request.form['email']
        influencer.category = request.form['category']
        influencer.niche = request.form['niche']
        influencer.reach = request.form['reach']
        influencer.platform = request.form['platform']
        influencer.bio = request.form['bio']
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('views.dashboard'))
    
    return render_template('influencer_update.html', influencer=influencer)

@auth.route('/search_campaigns', methods=['GET'])
@login_required
def search_campaigns():
    # Get the logged-in influencer's ID
    influencer = Influencer.query.filter_by(user_id=current_user.id).first()
    name = request.args.get('name')
    category = request.args.get('category')
    
    query = Campaign.query
    
    if name:
        query = query.filter(Campaign.name.ilike(f'%{name}%'))
    if category:
        query = query.filter(Campaign.niche.ilike(f'%{category}%'))
    
    campaigns = query.all()
    
    return render_template('search_campaign.html', campaigns=campaigns, influencer=influencer)

@auth.route('/send_influencer_to_campaign_request', methods=['POST'])
@login_required
def send_influencer_to_campaign_request():
    campaign_id = request.form.get('campaign_id')
    message = request.form.get('message')

    # Fetch the influencer corresponding to the current user
    influencer = Influencer.query.filter_by(user_id=current_user.id).first()

    # Ensure the current user is logged in and is an influencer
    if current_user.user_type != 'influencer':
        flash('Only influencers can send campaign requests.', 'danger')
        return redirect(url_for('auth.search_campaigns'))

    # Retrieve the Campaign based on campaign_id
    campaign = Campaign.query.filter_by(id=campaign_id).first()

    if not campaign:
        flash('Campaign not found.', 'danger')
        return redirect(url_for('auth.search_campaigns'))

    # Extract requirements and payment amount from the campaign
    requirements = campaign.goals
    payment_amount = campaign.budget

    new_request = CampaignRequest(
        campaign_id=campaign_id,
        influencer_id=influencer.id,
        messages=message,
        requirements=requirements,
        payment_amount=payment_amount,
        status='pending',
        completed=False,
        completion_confirmed=False,
        payment_done=False,
        rating_done=False
    )

    db.session.add(new_request)
    db.session.commit()

    flash('Request sent successfully!', 'success')
    return redirect(url_for('auth.search_campaigns'))

@auth.route('/sponsor_requests', methods=['GET'])
def sponsor_requests():
    requests = CampaignRequest.query.filter(
        CampaignRequest.campaign.has(user_id=current_user.id)
    ).all()
    
    total_requests = len(requests)
    
  
    return render_template('sponsor_request.html', requests=requests, total_requests=total_requests)

@auth.route('/send_ad_request', methods=['POST'])
@login_required
def send_ad_request():
    campaign_id = request.form.get('campaign_id')
    influencer_id = influencer_id
    message = request.form.get('message')

    # Retrieve the CampaignRequest based on campaign_id and influencer_id
    campaign_request = Campaign.query.filter_by(
        id=campaign_id
    ).first()
    
    if not campaign_request:
        flash('Campaign request not found.', 'danger')
        return redirect(url_for('auth.search_campaigns'))\

    # Create a new AdRequest with details from the CampaignRequest
    new_ad_request = AdRequest(
        campaign_id=campaign_request.id,
        influencer_id=influencer_id,
        messages=message,
        requirements=campaign_request.goals,
        payment_amount=campaign_request.budget,
        status='pending'
    )

    db.session.add(new_ad_request)
    db.session.commit()

    flash('Request sent successfully!', 'success')
    return redirect(url_for('auth.search_campaigns'))

@auth.route('/accept_request', methods=['POST'])
@login_required
def accept_request():
    request_id = request.form.get('request_id')
    # Logic to accept the request
    campaign_request = CampaignRequest.query.get(request_id)
    if campaign_request:
        campaign_request.status = 'accepted'
        db.session.commit()
        flash('Request accepted successfully.', 'success')
    else:
        flash('Request not found.', 'danger')
    return redirect(url_for('auth.sponsor_requests'))

@auth.route('/reject_request', methods=['POST'])
@login_required
def reject_request():
    request_id = request.form.get('request_id')
    # Logic to reject the request
    campaign_request = CampaignRequest.query.get(request_id)
    if campaign_request:
        campaign_request.status = 'rejected'
        db.session.commit()
        flash('Request rejected.', 'success')
    else:
        flash('Request not found.', 'danger')
    return redirect(url_for('auth.sponsor_requests'))

@auth.route('/send_sponsor_to_ad_request', methods=['POST'])
@login_required
def send_sponsor_to_ad_request():
    influencer_id = request.form.get('influencer_id')
    campaign_id = request.form.get('campaign_id')
    message = request.form.get('message')

    # Validate the campaign_id and influencer_id
    campaign = Campaign.query.get(campaign_id)
    influencer = Influencer.query.get(influencer_id)

    if not campaign or not influencer:
        flash("Invalid campaign or influencer.", "danger")
        return redirect(url_for('auth.search_influencers'))

    # Fetch campaign details (assuming these fields exist in your Campaign model)
    payment_amount = campaign.budget  
    requirements = campaign.goals 

    # Create a new AdRequest
    ad_request = AdRequest(
        influencer_id=influencer_id,
        campaign_id=campaign_id,
        payment_amount=payment_amount,
        requirements=requirements,
        messages=message,
        status='pending'  # Set default status if applicable
    )
    db.session.add(ad_request)
    db.session.commit()

    flash("Request submitted successfully!", "success")
    return redirect(url_for('auth.search_influencers'))

@auth.route('/accept_ad_request', methods=['POST'])
@login_required
def accept_ad_request():
    ad_request_id = request.form.get('ad_request_id')
    ad_request = AdRequest.query.get(ad_request_id)

    if ad_request:
        ad_request.status = 'accepted'
        db.session.commit()
        flash('Ad request accepted successfully!', 'success')
    else:
        flash('Ad request not found.', 'danger')

    return redirect(url_for('auth.ad_requests'))

@auth.route('/reject_ad_request', methods=['POST'])
@login_required
def reject_ad_request():
    ad_request_id = request.form.get('ad_request_id')
    ad_request = AdRequest.query.get(ad_request_id)

    if ad_request:
        ad_request.status = 'rejected'
        db.session.commit()
        flash('Ad request rejected successfully!', 'success')
    else:
        flash('Ad request not found.', 'danger')

    return redirect(url_for('auth.ad_requests'))

@auth.route('/ad_requests')
@login_required
def ad_requests():
    # Get the logged-in influencer's ID
    influencer = Influencer.query.filter_by(user_id=current_user.id).first()

    # If the user is not associated with an influencer, handle it appropriately
    if not influencer:
        flash('You are not associated with any influencer account.', 'danger')
        return redirect(url_for('main.dashboard'))

    # Fetch ad requests for the influencer
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id).all()

    return render_template('ad_requests.html', ad_requests=ad_requests, influencer=influencer)

@auth.route('/delete_ad_request', methods=['POST'])
@login_required
def delete_ad_request():
    ad_request_id = request.form.get('ad_request_id')
    ad_request = AdRequest.query.get(ad_request_id)

    if ad_request and ad_request.influencer_id == current_user.influencer.id:
        db.session.delete(ad_request)
        db.session.commit()
        flash('Ad request deleted.', 'danger')
    else:
        flash('Ad request not found or you are not authorized.', 'danger')

    return redirect(url_for('auth.ad_requests'))

@auth.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        username = request.form.get('username')
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('admin_signup'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(p_name=name, email=email, password=hashed_password, user_type='admin',p_username=username)

        db.session.add(new_user)
        db.session.commit()
        
        flash('Admin account created successfully!', 'success')
        return redirect(url_for('views.dashboard'))

    return render_template('admin_signup.html')

@auth.route('/manage_users')
@login_required
def manage_users():
    if current_user.user_type == 'admin':
        # Query users and join with the Influencer table if the user is an influencer
        users = db.session.query(User, Influencer).outerjoin(
            Influencer, User.id == Influencer.user_id
        ).filter(User.user_type.in_(['sponsor', 'influencer'])).all()
        
        # Prepare the users data
        user_data = []
        for user, influencer in users:
            user_info = {
                'id': user.id,
                'username': user.p_username,
                'email': user.email,
                'user_type': user.user_type,
                'flagged': user.flagged,
                'name': influencer.name if user.user_type == 'influencer' else user.p_name,
                'bio': influencer.bio if user.user_type == 'influencer' else user.p_bio,
                'count': influencer.reach if user.user_type == 'influencer' else user.p_count,
                'category': influencer.category if user.user_type == 'influencer' else user.p_category,
            }
            user_data.append(user_info)

        return render_template('manage_users.html', users=user_data)
    else:
        return redirect(url_for('dashboard'))
    

@auth.route('/edit_user', methods=['POST'])
@login_required
def edit_user():
    if current_user.user_type != 'admin':
        return redirect(url_for('dashboard'))

    user_id = request.form.get('user_id')
    username = request.form.get('username')
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')

    user = User.query.get(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('auth.manage_users'))

    user.p_username = username
    user.email = email

    if user.user_type == 'influencer':
        influencer = Influencer.query.filter_by(user_id=user.id).first()
        if influencer:
            influencer.name = name
    else:
        user.p_name = name

    if password:
        user.set_password(password)

    db.session.commit()

    flash("User details updated successfully.", "success")
    return redirect(url_for('auth.manage_users'))

@auth.route('/toggle_flag', methods=['POST'])
@login_required
def toggle_flag():
    if current_user.user_type != 'admin':
        return redirect(url_for('dashboard'))

    user_id = request.form.get('user_id')
    user = User.query.get(user_id)

    if not user:
        flash("User not found.", "danger")
        return redirect(url_for('auth.manage_users'))

    user.flagged = not user.flagged
    db.session.commit()

    if user.flagged:
        flash(f"User {user.p_username} has been flagged.", "warning")
    else:
        flash(f"User {user.p_username} has been unflagged.", "success")

    return redirect(url_for('auth.manage_users'))
