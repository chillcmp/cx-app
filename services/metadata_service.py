from sqlalchemy import func
from werkzeug.datastructures import FileStorage

from extensions.database import db
from models.image_metadata import ImageMetadata


class MetadataService:

    def get_metadata(self, filename: str) -> ImageMetadata:
        return ImageMetadata.query.filter_by(name=filename).first()

    def get_random_metadata(self):
        return ImageMetadata.query.order_by(func.rand()).first()

    def write_metadata(self, file: FileStorage):
        file.stream.seek(0, 2)
        size_in_bytes = file.stream.tell()
        file.stream.seek(0)

        metadata = ImageMetadata(
            name=file.filename,
            size=size_in_bytes,
            extension=file.content_type
        )
        db.session.add(metadata)
        db.session.commit()

    def delete_metadata(self, filename: str):
        record = self.get_metadata(filename)
        if record:
            db.session.delete(record)
            db.session.commit()
