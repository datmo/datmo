from flask import Flask
from flask import render_template

app = Flask(__name__)


@app.route("/")
def home():
    user = {"name": "test", "username": "test_username", "email": "test_email"}
    models = [{
        "id": "asdflkj",
        "name": "test_model",
        "categories": "cool, default",
        "repo_language": "python"
    }]
    return render_template("profile.html", user=user, models=models)


@app.route("/<model_id>")
def model_summary(model_id):
    user = {"name": "test", "username": "test_username", "email": "test_email"}
    snapshots = [
        {
            "id": "alfwokd",
            "created_at": "Sun March 3rd, 2018",
            "labels": ["cool", "default"],
            "config": {
                "algorithm": "random forest"
            },
            "stats": {
                "accuracy": 0.98
            }
        },
    ]
    config_keys = ["algorithm"]
    stats_keys = ["accuracy"]
    model = {
        "id": model_id,
        "name": "test_model",
        "categories": "cool, default",
        "repo_language": "python",
        "snapshots": snapshots
    }
    return render_template(
        "model_summary.html",
        user=user,
        model=model,
        snapshots=snapshots,
        config_keys=config_keys,
        stats_keys=stats_keys)


@app.route("/<model_id>/experiments")
def model_experiments(model_id):
    user = {"name": "test", "username": "test_username", "email": "test_email"}
    snapshots = [
        {
            "id": "alfwokd",
            "created_at": "Sun March 3rd, 2018",
            "labels": ["cool", "default"],
            "config": {
                "algorithm": "random forest"
            },
            "stats": {
                "accuracy": 0.98
            }
        },
    ]
    config_keys = ["algorithm"]
    stats_keys = ["accuracy"]
    model = {
        "id": model_id,
        "name": "test_model",
        "categories": "cool, default",
        "repo_language": "python",
        "snapshots": snapshots
    }
    return render_template(
        "model_experiments.html",
        user=user,
        model=model,
        snapshots=snapshots,
        config_keys=config_keys,
        stats_keys=stats_keys)


@app.route("/<model_id>/snapshots")
def model_snapshots(model_id):
    user = {"name": "test", "username": "test_username", "email": "test_email"}
    snapshots = [
        {
            "id": "alfwokd",
            "created_at": "Sun March 3rd, 2018",
            "labels": ["cool", "default"],
            "config": {
                "algorithm": "random forest"
            },
            "stats": {
                "accuracy": 0.98
            }
        },
    ]
    config_keys = ["algorithm"]
    stats_keys = ["accuracy"]
    model = {
        "id": model_id,
        "name": "test_model",
        "categories": "cool, default",
        "repo_language": "python",
        "snapshots": snapshots
    }
    return render_template(
        "model_snapshots.html",
        user=user,
        model=model,
        snapshots=snapshots,
        config_keys=config_keys,
        stats_keys=stats_keys)


@app.route("/<model_id>/deployments")
def model_deployments(model_id):
    user = {"name": "test", "username": "test_username", "email": "test_email"}
    snapshots = [
        {
            "id": "alfwokd",
            "created_at": "Sun March 3rd, 2018",
            "labels": ["cool", "default"],
            "config": {
                "algorithm": "random forest"
            },
            "stats": {
                "accuracy": 0.98
            }
        },
    ]
    config_keys = ["algorithm"]
    stats_keys = ["accuracy"]
    model = {
        "id": model_id,
        "name": "test_model",
        "categories": "cool, default",
        "repo_language": "python",
        "snapshots": snapshots
    }
    return render_template(
        "model_deployments.html",
        user=user,
        model=model,
        snapshots=snapshots,
        config_keys=config_keys,
        stats_keys=stats_keys)


if __name__ == "__main__":
    app.run(debug=True)
