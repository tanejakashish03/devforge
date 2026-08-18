from datetime import datetime, UTC

from app import db


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False, unique=True)

    repository_name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )

    github_repo_id = db.Column(
    db.BigInteger,
    nullable=True
    )

    github_repo_url = db.Column(
        db.String(500),
        nullable=True
    )

    application = db.Column(
        db.String(50),
        nullable=False
    )

    template_type = db.Column(
    db.String(30),
    nullable=False,
    default="flask"
    )
    
    visibility = db.Column(
        db.String(20),
        nullable=False,
        default="private"
    )

    port = db.Column(
        db.Integer,
        nullable=False,
        default=5000
    )

    health_endpoint = db.Column(
        db.String(100),
        nullable=False,
        default="/health"
    )

    environment = db.Column(
        db.String(30),
        nullable=False,
        default="development"
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="created"
    )

    version = db.Column(
        db.String(30),
        nullable=False,
        default="0.1.0"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(UTC)
    )

    def __repr__(self):
        return f"<Project {self.name}>"