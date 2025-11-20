"""Flask web application for Apartment Hunt Optimizer"""

from flask import Flask, render_template, request, jsonify
from database import get_all_apartments
from preferences import UserPreferences
from scoring import ApartmentScorer, filter_apartments
from geocoding import geocode_address_nominatim
import json

app = Flask(__name__)


@app.route('/')
def index():
    """Home page with preference form"""
    return render_template('index.html')


@app.route('/api/apartments')
def get_apartments():
    """API endpoint to get all apartments"""
    apartments = get_all_apartments(active_only=True)
    return jsonify({
        'success': True,
        'count': len(apartments),
        'apartments': apartments
    })


@app.route('/api/rank', methods=['POST'])
def rank_apartments():
    """API endpoint to rank apartments based on preferences"""
    try:
        data = request.json
        
        # Create preferences
        prefs = UserPreferences()
        
        # Set budget
        max_rent = int(data.get('max_rent', 2000))
        min_rent = int(data.get('min_rent', 0))
        prefs.set_budget(min_rent=min_rent, max_rent=max_rent)
        
        # Set space requirements
        min_bedrooms = float(data.get('min_bedrooms', 1))
        min_bathrooms = float(data.get('min_bathrooms', 1))
        min_sqft = int(data.get('min_sqft', 0))
        prefs.set_space_requirements(bedrooms=min_bedrooms, bathrooms=min_bathrooms, sqft=min_sqft)
        
        # Set work location if provided
        work_address = data.get('work_address', '').strip()
        if work_address:
            coords = geocode_address_nominatim(work_address)
            if coords:
                prefs.set_work_location(work_address, lat=coords[0], lng=coords[1])
            else:
                return jsonify({
                    'success': False,
                    'error': f'Could not geocode work address: {work_address}'
                }), 400
        
        # Get and filter apartments
        listings = get_all_apartments(active_only=True)
        filtered = filter_apartments(listings, prefs)
        
        if not filtered:
            return jsonify({
                'success': True,
                'message': 'No apartments match your criteria',
                'apartments': [],
                'count': 0
            })
        
        # Score apartments
        scorer = ApartmentScorer(prefs)
        ranked = []
        
        for listing in filtered:
            score_data = scorer.score_apartment(listing)
            ranked.append({
                'listing': listing,
                'score': score_data['total_score'],
                'breakdown': score_data['breakdown'],
                'commute_info': score_data['commute_info']
            })
        
        # Sort by score
        ranked.sort(key=lambda x: x['score'], reverse=True)
        
        return jsonify({
            'success': True,
            'apartments': ranked,
            'count': len(ranked),
            'preferences': prefs.to_dict()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/geocode')
def geocode():
    """API endpoint to geocode an address"""
    address = request.args.get('address', '')
    
    if not address:
        return jsonify({
            'success': False,
            'error': 'No address provided'
        }), 400
    
    coords = geocode_address_nominatim(address)
    
    if coords:
        return jsonify({
            'success': True,
            'latitude': coords[0],
            'longitude': coords[1],
            'address': address
        })
    else:
        return jsonify({
            'success': False,
            'error': 'Could not geocode address'
        }), 404


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
