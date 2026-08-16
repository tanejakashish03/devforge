from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
)

from app import db
from app.models.project import Project


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