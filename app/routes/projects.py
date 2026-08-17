from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
)

from app import db
from app.models.project import Project
from app.services.github_service import create_repository


projects_bp = Blueprint(
    "projects",
    __name__,
    url_prefix="/projects"
)


@projects_bp.route("/create", methods=["GET", "POST"])
def create_project():

    if request.method == "POST":

        project = Project(
            name=request.form["name"],
            repository_name=request.form["repository_name"],
            application=request.form["application"],
            visibility=request.form["visibility"],
            port=int(request.form["port"]),
            health_endpoint=request.form["health_endpoint"],
            environment=request.form["environment"],
        )

        db.session.add(project)
        db.session.commit()

        return redirect(url_for("main.dashboard"))

    return render_template("create_project.html")


@projects_bp.route("/<int:project_id>/github", methods=["POST"])
def create_github_repository(project_id):
    project = db.session.get(Project, project_id)

    if project is None:
        return {"error": "Project not found"}, 404

    if project.github_repo_url:
        return redirect(
            url_for(
                "main.dashboard",
                github="exists",
                project=project.id,
            )
        )

    repository = create_repository(
        name=project.repository_name,
        description=f"DevForge project: {project.name}",
        private=project.visibility == "private",
    )

    project.github_repo_id = repository["id"]
    project.github_repo_url = repository["html_url"]

    db.session.commit()

    return redirect(
        url_for(
            "main.dashboard",
            github="created",
            project=project.id,
        )
    )