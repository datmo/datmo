import os
import uuid
import json
from flask import Flask
from flask import render_template, request, jsonify
import plotly
from datetime import datetime

from datmo.monitoring import Monitoring

app = Flask(__name__)
# TODO: pull api_key from global config
datmo_monitoring = Monitoring(api_key="6a3a3cd900eaf7b406a41d68f8ca7969")


@app.route("/")
def home():
    user = {
        "name":
            "Shabaz Patel",
        "username":
            "shabazp",
        "email":
            "shabaz@datmo.com",
        "gravatar_url":
            "https://www.gravatar.com/avatar/" + str(uuid.uuid1()) +
            "?s=220&d=identicon&r=PG"
    }
    models = [{
        "id": "credit_fraud",
        "name": "Credit Fraud",
        "categories": "",
        "repo_language": "python"
    }]
    return render_template("profile.html", user=user, models=models)


@app.route("/<model_id>")
def model_summary(model_id):
    user = {
        "name":
            "Shabaz Patel",
        "username":
            "shabazp",
        "email":
            "shabaz@datmo.com",
        "gravatar_url":
            "https://www.gravatar.com/avatar/" + str(uuid.uuid1()) +
            "?s=220&d=identicon&r=PG"
    }
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
        "name": "Credit Fraud",
        "categories": "",
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
    user = {
        "name":
            "Shabaz Patel",
        "username":
            "shabazp",
        "email":
            "shabaz@datmo.com",
        "gravatar_url":
            "https://www.gravatar.com/avatar/" + str(uuid.uuid1()) +
            "?s=220&d=identicon&r=PG"
    }
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
        "name": "Credit Fraud",
        "categories": "",
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
    user = {
        "name":
            "Shabaz Patel",
        "username":
            "shabazp",
        "email":
            "shabaz@datmo.com",
        "gravatar_url":
            "https://www.gravatar.com/avatar/" + str(uuid.uuid1()) +
            "?s=220&d=identicon&r=PG"
    }
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
        "name": "Credit Fraud",
        "categories": "",
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


@app.route(
    "/data/<model_id>/deployments/<deployment_version_id>/<model_version_id>")
def model_deployment_data(model_id, deployment_version_id, model_version_id):
    # here we want to get the value of user (i.e. ?start=0)
    start = request.args.get('start', 0)
    count = request.args.get('count', 100)
    data_type = request.args.get('data_type', None)
    name = request.args.get('name', None)
    graph_type = request.args.get('graph_type', None)

    if not data_type and not name and not graph_type:
        return "error", 400

    # Get new data to add to the graphs
    filter = {
        "model_id": model_id,
        "deployment_version_id": deployment_version_id,
        "model_version_id": model_version_id,
        "start": int(start),
        "count": int(count)
    }
    new_data = datmo_monitoring.search_metadata(filter)

    # update the number of new results
    num_new_results = len(new_data)

    # return error if data_type is not correct
    if data_type not in ["input", "prediction", "feedback"]:
        return "error", 400

    # populate the data into the correct construct based on graph type
    if graph_type == "timeseries":
        new_time_data = [
            datum['updated_at'] if datum['updated_at'] else datum['created_at']
            for datum in new_data
        ]
        new_time_data_datetime = [
            datetime.fromtimestamp(
                float(t) / 1000).strftime('%Y-%m-%d %H:%M:%S')
            for t in new_time_data
        ]
        new_feature_data = [
            datum[data_type][name] if datum[data_type] else None
            for datum in new_data
        ]
        graph_data_output = {
            "new_data": {
                "x": [new_time_data_datetime],
                "y": [new_feature_data],
            }
        }

    elif graph_type == "histogram":
        filter = {
            "model_id": model_id,
            "deployment_version_id": deployment_version_id,
            "model_version_id": model_version_id,
            "count": int(start) + int(count)
        }
        cumulative_data = datmo_monitoring.search_metadata(filter)
        cumulative_feature_data = [
            datum[data_type][name] for datum in cumulative_data
            if datum[data_type]
        ]
        import numpy as np
        counts, binedges = np.histogram(cumulative_feature_data)
        binsize = binedges[1] - binedges[0]
        bin_names = [
            str(round(binedge, 2)) + " : " + str(round(binedge + binsize, 2))
            for binedge in binedges
        ]
        graph_data_output = {
            "cumulative_data": {
                "x": [bin_names],
                "y": [counts]
            }
        }
    else:
        return "error", 400

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graph_data_outputJSON = json.dumps(
        graph_data_output, cls=plotly.utils.PlotlyJSONEncoder)

    return jsonify(
        graph_data_output_json_str=graph_data_outputJSON,
        num_new_results=num_new_results)


@app.route(
    "/<model_id>/deployments/<deployment_version_id>/<model_version_id>")
def model_deployment_detail(model_id, deployment_version_id, model_version_id):
    user = {
        "name":
            "Shabaz Patel",
        "username":
            "shabazp",
        "email":
            "shabaz@datmo.com",
        "gravatar_url":
            "https://www.gravatar.com/avatar/" + str(uuid.uuid1()) +
            "?s=220&d=identicon&r=PG"
    }
    model = {
        "id": model_id,
        "name": "Credit Fraud",
        "categories": "",
        "repo_language": "python"
    }

    filter = {
        "model_id": model_id,
        "model_version_id": model_version_id,
        "deployment_version_id": deployment_version_id
    }
    input_keys, prediction_keys, feedback_keys = [], [], []
    data = datmo_monitoring.search_metadata(filter)

    if data:
        max_index = 0
        for ind, datum in enumerate(data):
            if datum['feedback'] is not None:
                max_index = ind
        datum = data[max_index]
        input_keys = list(datum['input'].keys())
        prediction_keys = list(datum['prediction'].keys())
        feedback_keys = list(
            datum['feedback'].keys()) if datum['feedback'] is not None else []

    return render_template(
        "model_deployment_detail.html",
        user=user,
        model=model,
        model_version_id=model_version_id,
        deployment_version_id=deployment_version_id,
        input_keys=input_keys,
        prediction_keys=prediction_keys,
        feedback_keys=feedback_keys)


@app.route("/<model_id>/deployments")
def model_deployments(model_id):
    user = {
        "name":
            "Shabaz Patel",
        "username":
            "shabazp",
        "email":
            "shabaz@datmo.com",
        "gravatar_url":
            "https://www.gravatar.com/avatar/" + str(uuid.uuid1()) +
            "?s=220&d=identicon&r=PG"
    }
    model = {
        "id": model_id,
        "name": "Credit Fraud",
        "categories": "",
        "repo_language": "python"
    }

    # get all data and extract unique model_version_id and deployment_version_id
    filter = {"model_id": model_id}

    all_data = datmo_monitoring.search_metadata(filter)
    model_version_ids = set(data['model_version_id'] for data in all_data)
    deployment_version_ids = set(
        data['deployment_version_id'] for data in all_data)

    # Get deployment information for each of the deployments
    deployments = []
    for deployment_version_id in deployment_version_ids:
        for model_version_id in model_version_ids:
            try:
                deployment_info = datmo_monitoring.get_deployment_info(
                    deployment_version_id=deployment_version_id)
            except:
                break
            # TODO: replace with proper handling
            deployment_info['endpoints'] = [
                endpoint for endpoint in deployment_info['endpoints']
                if "".join(model_version_id.split("_")) in endpoint
            ]
            deployment_info['service_paths'] = [
                path for path in deployment_info['service_paths']
                if "".join(model_version_id.split("_")) in path
            ]
            # TODO: END
            deployment_info['deployment_version_id'] = deployment_version_id
            deployment_info['model_version_id'] = model_version_id
            deployments.append(deployment_info)

    # Get the data here (hard coded)
    # TODO: generalize

    # based on the model_version_id and deployment_version_id the user selects
    # show various graphs

    return render_template(
        "model_deployments.html",
        user=user,
        model=model,
        deployments=deployments,
    )


@app.route(
    "/<model_id>/deployments/<deployment_version_id>/<model_version_id>/script/create"
)
def model_deployment_script_create(model_id, deployment_version_id,
                                   model_version_id):
    content = request.args.get('content')
    # TODO: Create a default location to save for the specific deployment
    filepath = request.args.get('filepath')
    with open(filepath, "w") as f:
        f.write(content)
    return "complete", 200


@app.route(
    "/<model_id>/deployments/<deployment_version_id>/<model_version_id>/script/run"
)
def model_deployment_script_run(model_id, deployment_version_id,
                                model_version_id):
    # TODO: Create a default location to save for the specific deployment
    filepath = request.args.get('filepath')
    os.system("python " + filepath)
    return "complete", 200


if __name__ == "__main__":
    app.run(debug=True)
