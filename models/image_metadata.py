from extensions.database import db
from datetime import datetime, timezone


class ImageMetadata(db.Model):
    __tablename__ = 'image_metadata'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    size = db.Column(db.Integer, nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.now(timezone.utc))
    extension = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "size": self.size,
            "upload_date": self.upload_date.isoformat(),
            "extension": self.extension
        }
