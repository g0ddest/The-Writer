from app import db



class User(db.Document):
    login = db.StringField(unique = True)
    password = db.BinaryField()
    name = db.StringField()
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return unicode(self.id)
    
    def __repr__(self):
        return '<User %r>' % (self.login)

#for a in User.objects.all():
#    a.delete()
#
#User(login = "admin", name = "Admin", password="").save()
#
#print User.objects.all()