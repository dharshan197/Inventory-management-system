from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key'

db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class ProductMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    from_location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    to_location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    from_location = db.relationship('Location', foreign_keys=[from_location_id])
    to_location = db.relationship('Location', foreign_keys=[to_location_id])
    product = db.relationship('Product')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/products', methods=['GET', 'POST'])
def manage_products():
    if request.method == 'POST':
        try:
            product_id = request.form.get('product_id')
            name = request.form.get('name')
            if not name:
                flash('Product name is required.', 'danger')
                return redirect(url_for('manage_products'))
            if product_id:
                product = Product.query.get_or_404(product_id)
                product.name = name
                flash('Product updated successfully!', 'success')
            else:
                db.session.add(Product(name=name))
                flash('Product added successfully!', 'success')
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('manage_products'))

    products = Product.query.all()
    return render_template('products.html', products=products)

@app.route('/locations', methods=['GET', 'POST'])
def manage_locations():
    if request.method == 'POST':
        try:
            location_id = request.form.get('location_id')
            name = request.form.get('name')
            if not name:
                flash('Location name is required.', 'danger')
                return redirect(url_for('manage_locations'))
            if location_id:
                location = Location.query.get_or_404(location_id)
                location.name = name
                flash('Location updated successfully!', 'success')
            else:
                db.session.add(Location(name=name))
                flash('Location added successfully!', 'success')
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('manage_locations'))

    locations = Location.query.all()
    return render_template('locations.html', locations=locations)

@app.route('/movements', methods=['GET', 'POST'])
def manage_movements():
    if request.method == 'POST':
        try:
            product_id = request.form.get('product_id')
            from_location_id = request.form.get('from_location_id') or None
            to_location_id = request.form.get('to_location_id') or None
            quantity = request.form.get('quantity')

            if not product_id or not quantity:
                flash('All fields are required.', 'danger')
            else:
                movement = ProductMovement(
                    product_id=product_id,
                    from_location_id=from_location_id,
                    to_location_id=to_location_id,
                    quantity=quantity
                )
                db.session.add(movement)
                db.session.commit()
                flash('Movement added successfully!', 'success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('manage_movements'))

    movements = ProductMovement.query.all()
    products = Product.query.all()
    locations = Location.query.all()
    return render_template('movements.html', movements=movements, products=products, locations=locations, movement=None)

@app.route('/edit_movement/<int:id>', methods=['GET', 'POST'])
def edit_movement(id):
    movement = ProductMovement.query.get_or_404(id)
    products = Product.query.all()
    locations = Location.query.all()

    if request.method == 'POST':
        try:
            movement.product_id = request.form.get('product_id')
            movement.from_location_id = request.form.get('from_location_id') or None
            movement.to_location_id = request.form.get('to_location_id') or None
            movement.quantity = request.form.get('quantity')

            db.session.commit()
            flash('Movement updated successfully!', 'success')
            return redirect(url_for('manage_movements'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error updating movement: {str(e)}', 'danger')

    return render_template('edit_movement.html', movement=movement, products=products, locations=locations)

@app.route('/report')
def report():
    report_data = []
    try:
        products = Product.query.all()
        locations = Location.query.all()

        for product in products:
            for location in locations:
                incoming = db.session.query(db.func.sum(ProductMovement.quantity)).filter(
                    ProductMovement.product_id == product.id,
                    ProductMovement.to_location_id == location.id
                ).scalar() or 0
                outgoing = db.session.query(db.func.sum(ProductMovement.quantity)).filter(
                    ProductMovement.product_id == product.id,
                    ProductMovement.from_location_id == location.id
                ).scalar() or 0
                balance = incoming - outgoing
                if balance > 0:
                    report_data.append({
                        'product': product.name,
                        'location': location.name,
                        'quantity': balance
                    })
    except SQLAlchemyError as e:
        flash(f'Error generating report: {str(e)}', 'danger')

    return render_template('report.html', report_data=report_data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
