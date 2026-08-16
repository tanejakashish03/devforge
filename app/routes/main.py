from flask import Blueprint, render_template

from app.models.project import Project


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():

    projects = Project.query.order_by(
        Project.created_at.desc()
    ).all()

    project_count = len(projects)

    deployment_count = 0

    healthy_count = sum(
        1
        for project in projects
        if project.status == "healthy"
    )

    return render_template(
        "dashboard.html",
        projects=projects,
        project_count=project_count,
        deployment_count=deployment_count,
        healthy_count=healthy_count,
    )