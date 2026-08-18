import tempfile

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
)

from app import db
from app.models.project import Project
from sqlalchemy.exc import IntegrityError

from app.services.github_service import (
    create_repository,
    get_repository,
    get_authenticated_user,
    upload_project_directory,
    delete_repository,
)

from app.services.generator_service import (
    SUPPORTED_TEMPLATES,
    generate_project,
)


projects_bp = Blueprint(
    "projects",
    __name__,
    url_prefix="/projects"
)


@projects_bp.route("/create", methods=["GET", "POST"])
def create_project():

    if request.method == "POST":

        template_type = request.form["application"]
        repository_name = request.form["repository_name"].strip()

        if template_type not in SUPPORTED_TEMPLATES:
            return {
                "error": "Unsupported application template"
            }, 400

        existing_project = Project.query.filter_by(
            repository_name=repository_name
        ).first()

        if existing_project:
            return render_template(
                "create_project.html",
                error=(
                    "A project with this repository name already exists "
                    "in DevForge. Please choose a different repository name."
                ),
            ), 409

        project = Project(
            name=request.form["name"],
            repository_name=repository_name,
            application=template_type,
            template_type=template_type,
            visibility=request.form["visibility"],
            port=int(request.form["port"]),
            health_endpoint=request.form["health_endpoint"],
            environment=request.form["environment"],
        )

        db.session.add(project)

        try:
            db.session.commit()

        except IntegrityError:
            db.session.rollback()

            return render_template(
                "create_project.html",
                error=(
                    "A project with this repository name already exists "
                    "in DevForge. Please choose a different repository name."
                ),
            ), 409

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

    result = create_repository(
        name=project.repository_name,
        description=f"DevForge project: {project.name}",
        private=project.visibility == "private",
    )

    repository = result["repository"]

    if result["status"] == "exists":
        return render_template(
            "existing_repository.html",
            project=project,
            repository=repository,
        )

    project.github_repo_id = repository["id"]
    project.github_repo_url = repository["html_url"]

    owner = repository["owner"]["login"]

    with tempfile.TemporaryDirectory() as temp_directory:
        generate_project(
            template_type=project.template_type,
            destination=temp_directory,
        )

        upload_project_directory(
            owner=owner,
            repository_name=project.repository_name,
            source_directory=temp_directory,
        )

    db.session.commit()

    return redirect(
        url_for(
            "main.dashboard",
            github="created",
            project=project.id,
        )
    )


@projects_bp.route(
    "/<int:project_id>/github/link",
    methods=["POST"],
)
def link_existing_repository(project_id):
    project = db.session.get(Project, project_id)

    if project is None:
        return {"error": "Project not found"}, 404

    if project.github_repo_url:
        return redirect(
            url_for("main.dashboard")
        )

    user = get_authenticated_user()

    repository = get_repository(
        owner=user["login"],
        repository_name=project.repository_name,
    )

    project.github_repo_id = repository["id"]
    project.github_repo_url = repository["html_url"]

    db.session.commit()

    return redirect(
        url_for(
            "main.dashboard",
            github="linked",
            project=project.id,
        )
    )


@projects_bp.route(
    "/<int:project_id>/github/discard",
    methods=["POST"],
)
def discard_project(project_id):
    project = db.session.get(Project, project_id)

    if project is None:
        return {"error": "Project not found"}, 404

    db.session.delete(project)
    db.session.commit()

    return redirect(
        url_for(
            "main.dashboard",
            github="discarded",
        )
    )



@projects_bp.route("/<int:project_id>/delete", methods=["POST"])
def delete_project(project_id):

    project = db.session.get(Project, project_id)

    if project is None:
        return {
            "error": "Project not found"
        }, 404

    delete_github = (
        request.form.get("delete_github") == "true"
    )

    if delete_github:

        if project.github_repo_url:

            owner = project.github_repo_url.rstrip(
                "/"
            ).split("/")[-2]

            try:

                delete_repository(
                    owner=owner,
                    repository_name=project.repository_name,
                )

            except RuntimeError:

                return redirect(
                    url_for(
                        "main.dashboard",
                        github="delete_failed",
                        project=project.id,
                    )
                )

    db.session.delete(project)

    db.session.commit()

    if delete_github:

        return redirect(
            url_for(
                "main.dashboard",
                github="deleted",
                project=project.id,
            )
        )

    return redirect(
        url_for(
            "main.dashboard",
            github="discarded",
            project=project.id,
        )
    )