from flask import Blueprint, render_template

from app.models.project import Project


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():

    projects = Project.query.order_by(
        Project.created_at.desc()
    ).all()

    project_count = len(projects)

    healthy_count = sum(
        1
        for project in projects
        if project.status == "healthy"
    )

    pipeline_stages = [
        {
            "name": "Project",
            "tools": "Flask · FastAPI · Node.js",
            "description": (
                "Generate a ready-to-use application from a DevForge template."
            ),
        },
        {
            "name": "Source Control",
            "tools": "GitHub",
            "description": (
                "Create or link the project's GitHub repository and upload "
                "the generated source."
            ),
        },
        {
            "name": "CI/CD",
            "tools": "GitHub Actions · Jenkins · GitLab CI",
            "description": (
                "Provide automated pipeline definitions for testing and "
                "application delivery across multiple CI/CD platforms."
            ),
        },
        {
            "name": "Quality & Security",
            "tools": "Pytest · SonarQube · Trivy",
            "description": (
                "Test applications and provide code-quality and "
                "container-security checks."
            ),
        },
        {
            "name": "Container",
            "tools": "Docker · GitHub Container Registry",
            "description": (
                "Package applications as container images and support "
                "registry-based delivery."
            ),
        },
        {
            "name": "Infrastructure",
            "tools": "Terraform · AWS",
            "description": (
                "Provision the AWS infrastructure used by the "
                "deployment environment."
            ),
        },
        {
            "name": "Deployment",
            "tools": "Ansible · Docker · NGINX · Blue/Green",
            "description": (
                "Configure the server and run blue-green application "
                "environments behind NGINX."
            ),
        },
        {
            "name": "Monitoring",
            "tools": "Prometheus · Grafana · Node Exporter",
            "description": (
                "Collect application and host metrics from the "
                "deployed environment."
            ),
        },
    ]

    return render_template(
        "dashboard.html",
        projects=projects,
        project_count=project_count,
        healthy_count=healthy_count,
        pipeline_stages=pipeline_stages,
    )
