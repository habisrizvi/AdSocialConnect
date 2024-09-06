from flask_login import UserMixin
from . import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    p_name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    user_type = db.Column(db.String(20))  # 'admin', 'sponsor'
    p_category = db.Column(db.String(150))
    p_count = db.Column(db.String(150))
    p_bio = db.Column(db.String(150))
    p_username = db.Column(db.String(150), unique=True)
    flagged = db.Column(db.Boolean, default=False)

    campaigns = relationship('Campaign', back_populates='user')
    influencer = relationship('Influencer', back_populates='user', uselist=False)

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.String, nullable=False)
    end_date = db.Column(db.String, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    visibility = db.Column(db.String(20))  # e.g., 'public', 'private'
    goals = db.Column(db.Text)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    niche = db.Column(db.String(150))
    status = db.Column(db.String(20), default="active")  # e.g., 'active', 'completed', 'paused'
    flagged = db.Column(db.Boolean, default=False)

    user = relationship('User', back_populates='campaigns')
    requests = relationship('CampaignRequest', back_populates='campaign')
    ad_requests = relationship('AdRequest', back_populates='campaign')

class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    category = db.Column(db.String(250))
    niche = db.Column(db.String(150))
    reach = db.Column(db.Integer)
    user_id = db.Column(db.Integer, ForeignKey('user.id'), nullable=False)
    platform = db.Column(db.String(150))
    bank_account_balance = db.Column(db.Float, default=0.0)
    bio = db.Column(db.String(150))

    user = relationship('User', back_populates='influencer')
    requests = relationship('CampaignRequest', back_populates='influencer')
    ad_requests = relationship('AdRequest', back_populates='influencer')

class CampaignRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, ForeignKey('influencer.id'), nullable=False)
    messages = db.Column(db.Text)  # Messages between sponsor and influencer
    requirements = db.Column(db.Text)  # Specific requirements for the campaign
    payment_amount = db.Column(db.Float)  # Agreed payment amount
    status = db.Column(db.String(50))  # Status of the request (e.g., 'pending', 'accepted', 'rejected')
    completed = db.Column(db.Boolean, default=False)  # If the campaign has been completed
    completion_confirmed = db.Column(db.Boolean, default=False)  # If the completion has been confirmed
    payment_done = db.Column(db.Boolean, default=False)  # If payment has been done
    rating_done = db.Column(db.Boolean, default=False)  # If rating has been provided

    campaign = relationship('Campaign', back_populates='requests')
    influencer = relationship('Influencer', back_populates='requests')

class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, ForeignKey('influencer.id'), nullable=False)
    messages = db.Column(db.Text)  # Messages between sponsor and influencer
    requirements = db.Column(db.Text)  # Specific requirements for the ad campaign
    payment_amount = db.Column(db.Float)  # Agreed payment amount
    status = db.Column(db.String(50))  # Status of the ad request (e.g., 'pending', 'accepted', 'rejected')
    completed = db.Column(db.Boolean, default=False)  # If the ad campaign has been completed
    completion_confirmed = db.Column(db.Boolean, default=False)  # If the completion has been confirmed
    payment_done = db.Column(db.Boolean, default=False)  # If payment has been done
    rating_done = db.Column(db.Boolean, default=False)  # If rating has been provided

    campaign = relationship('Campaign', back_populates='ad_requests')
    influencer = relationship('Influencer', back_populates='ad_requests')

