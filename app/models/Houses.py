from app import db
from uuid import uuid1 as uuid
class HouseDetail(db.Model):
    __tablename__ = 'house_detail'
    id=db.Column(db.String(32),primary_key=True)
    presale_num = db.Column(db.String(64),default="")
    building_num = db.Column(db.String(64))
    room_num = db.Column(db.String(64))
    floor_area = db.Column(db.Float)
    use_area = db.Column(db.Float)
    used_precent = db.Column(db.Float)
    unit_price = db.Column(db.Float)
    decorate_price = db.Column(db.Float)
    total_price = db.Column(db.Float)
    house = db.Column(db.String(32),db.ForeignKey('houses.id'))
    def save(self):
        if not self.id:
            self.id = uuid().hex
        db.session.add(self)
        db.session.commit()


class Houses(db.Model):
    __tablename__ = 'houses'
    id = db.Column(db.String(32),primary_key=True)
    url = db.Column(db.String(255))
    name = db.Column(db.String(64))
    details = db.relationship('HouseDetail',backref='houseinfo')
    def save(self):
        if not self.id:
            self.id = uuid().hex
        db.session.add(self)
        db.session.commit()