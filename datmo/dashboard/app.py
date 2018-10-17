import json
from flask import Flask
from flask import render_template, jsonify

from datmo.monitoring import Monitoring

app = Flask(__name__)
# TODO: pull api_key from global config
datmo_monitoring = Monitoring(api_key="d41d8cd98f00b204e9800998ecf8427e")


@app.route("/")
def home():
    user = {"name": "test", "username": "test_username", "email": "test_email"}
    models = [{
        "id": "anand_test",
        "name": "anand_test",
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
        "name": "anand_test",
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
        "name": "anand_test",
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
        "name": "anand_test",
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
        "name": "anand_test",
        "categories": "cool, default",
        "repo_language": "python",
        "snapshots": snapshots
    }

    # Get the data here (hard coded)
    # TODO: generalize

    # get all data and extract unique model_version_id and deployment_version_id
    filter = {"model_id": model_id}

    all_data = datmo_monitoring.search_metadata(filter)
    model_version_ids = list(
        set(data['model_version_id'] for data in all_data))
    deployment_version_ids = list(
        set(data['deployment_version_id'] for data in all_data))

    # Get deployment information for each of the deployments
    deployments = []
    for deployment_version_id, model_version_id in zip(deployment_version_ids,
                                                       model_version_ids):
        deployment_info = datmo_monitoring.get_deployment_info(
            deployment_version_id=deployment_version_id)
        deployment_info['deployment_version_id'] = deployment_version_id
        deployment_info['model_version_id'] = model_version_id
        deployments.append(deployment_info)

    # based on the model_version_id and deployment_version_id the user selects
    # show various graphs

    filter = {
        "model_id": model_id,
        "model_version_id": "first",
        "deployment_version_id": "restful"
    }
    data = datmo_monitoring.search_metadata(filter)
    data = json.dumps(data)

    return render_template(
        "model_deployments.html",
        user=user,
        model=model,
        snapshots=snapshots,
        config_keys=config_keys,
        stats_keys=stats_keys,
        deployments=deployments,
        data=data)


if __name__ == "__main__":
    app.run(debug=True)
