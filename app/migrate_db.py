from models import db, Property, User

def create_data():
    # Create all tables
    db.create_all()

    # Create a new user
    new_user = User(username="soul2323", email="pauling23@gmail.com", password="passjdkdj923")
    db.session.add(new_user)
    db.session.commit()

    # Create a new property
    new_property = Property(title="New Property", description="New real estate listing ", price=120000, location="Kaunas", user_id=new_user.id)
    db.session.add(new_property)
    db.session.commit()

    # Query all properties
    properties = Property.query.all()
    for property in properties:
        print(property)


# if __name__ == "__main__":
#
#     app = create_app()
#     with app.app_context():
#         create_data()



