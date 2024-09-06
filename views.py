from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from .models import *
import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot
import matplotlib.pyplot as plt
import os


views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html', user=current_user)

@views.route('/dashboard')
@login_required
def dashboard():
    user_type = current_user.user_type
    if user_type == 'admin':
        total_influencers = User.query.filter_by(user_type='influencer').count()
        total_sponsors = User.query.filter_by(user_type='sponsor').count()
        total_users = User.query.count()
        total_campaigns = Campaign.query.count()
        total_ad_requests = AdRequest.query.count()
        
        # Generate the user distribution pie chart
        labels = 'Influencers', 'Sponsors'
        sizes = [total_influencers, total_sponsors]
        colors = ['#ff9999', '#66b3ff']
        explode = (0.1, 0)  # explode 1st slice

        fig1, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        plt.title('User Distribution')
        plt.tight_layout()

        user_dist_path = os.path.join(current_app.root_path, 'static/images/user_distribution.png')
        plt.savefig(user_dist_path)
        plt.close(fig1)
        
        
        
        
         # Generate the user distribution pie chart
        labels = 'Influencers', 'Sponsors'
        sizes = [total_campaigns, total_sponsors]
        colors = ['#ff9999', '#66b3ff']
        explode = (0.1, 0)  # explode 1st slice

        fig3, ax1 = plt.subplots()
        ax1.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        plt.title('User Distribution')
        plt.tight_layout()

        user_dist_path = os.path.join(current_app.root_path, 'static/images/user_distribution24.png')
        plt.savefig(user_dist_path)
        plt.close(fig3)
        
        
        
        
        
        
        

        # Generate the campaign distribution pie chart
        labels = 'Campaigns', 'Ad Requests', 'Others'
        sizes = [total_campaigns, total_ad_requests, total_users - total_campaigns - total_ad_requests]
        colors = ['#ff9999', '#66b3ff', '#99ff99']
        explode = (0.1, 0, 0)  # explode 1st slice

        fig2, ax2 = plt.subplots()
        ax2.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax2.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

        plt.title('Campaigns and Requests Distribution')
        plt.tight_layout()

        campaign_dist_path = os.path.join(current_app.root_path, 'static/images/campaign_distribution.png')
        plt.savefig(campaign_dist_path)
        plt.close(fig2)

        return render_template('profile_overview.html', 
                               user=current_user, 
                               total_influencers=total_influencers, 
                               total_sponsors=total_sponsors, 
                               total_users=total_users, 
                               total_campaigns=total_campaigns, 
                               total_ad_requests=total_ad_requests,
                               url1="images/user_distribution.png",
                               url2="images/campaign_distribution.png",
                               url3='/images/user_distribution24.png')
    elif current_user.user_type == 'influencer':
        # Fetch the influencer record based on the logged-in user's ID
        influencer = Influencer.query.filter_by(user_id=current_user.id).first()

        # Initialize campaigns list to store the campaigns associated with this influencer
        campaigns = []

        if influencer:
            # Fetch campaigns from the CampaignRequest table where the influencer is involved and the request is accepted
            campaign_requests = CampaignRequest.query.filter_by(influencer_id=influencer.id, status='accepted').all()

            # Fetch campaigns from the AdRequest table where the influencer is involved and the request is accepted
            ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id, status='accepted').all()

            # Use sets to ensure unique campaigns are displayed
            campaign_ids = set([request.campaign_id for request in campaign_requests])
            ad_campaign_ids = set([request.campaign_id for request in ad_requests])

            # Combine both sets to ensure unique campaign IDs
            unique_campaign_ids = campaign_ids.union(ad_campaign_ids)

            # Fetch the campaigns based on the unique campaign_ids
            campaigns = Campaign.query.filter(Campaign.id.in_(unique_campaign_ids)).all()

        # Render the profile overview template, passing the influencer and their campaigns
        return render_template('profile_overview.html', influencer=influencer, campaigns=campaigns)
        
    else:
        return render_template('profile_overview.html', user=current_user)


@views.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
