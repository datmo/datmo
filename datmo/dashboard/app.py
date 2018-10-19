import uuid
import json
import random
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
        "categories": "cool, default",
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


@app.route("/data/<model_id>/<deployment_version_id>")
def model_deployment_data(model_id, deployment_version_id):
    # here we want to get the value of user (i.e. ?start=0)
    start = request.args.get('start', 0)
    count = request.args.get('count', 10)
    num_features = request.args.get('num_features', 0)
    filter = {
        "model_id": model_id,
        "deployment_version_id": deployment_version_id,
        "start": int(start),
        "count": int(count)
    }
    num_new_results = 0
    new_data = datmo_monitoring.search_metadata(filter)

    filter = {
        "model_id": model_id,
        "deployment_version_id": deployment_version_id,
        "count": int(start) + int(count)
    }
    cumulative_data = datmo_monitoring.search_metadata(filter)

    time_series_graphs_extension = []
    histogram_graphs_update = []
    if new_data:
        num_new_results = len(new_data)
        # Extract all inputs, predictions, and actual keys
        datum = new_data[0]
        input_features = datum['input'].keys()
        prediction_features = datum['prediction'].keys()
        feedback_features = datum['feedback'].keys() if datum[
            'feedback'] else []
        num_feedback_features = int(num_features) - len(input_features) - len(
            prediction_features)

        # Loop through input and predictions to populate the graphs
        new_time_data = [datum['created_at'] for datum in new_data]
        new_time_data_datetime = [
            datetime.fromtimestamp(
                float(t) / 1000).strftime('%Y-%m-%d %H:%M:%S')
            for t in new_time_data
        ]

        for prediction_feature in prediction_features:
            # time series data chart
            new_feature_data = [
                datum['prediction'][prediction_feature] for datum in new_data
            ]
            time_series_graphs_extension.append({
                "new_data": {
                    "x": [new_time_data_datetime],
                    "y": [new_feature_data],
                }
            })

            # histogram data chart
            cumulative_feature_data = [
                datum['prediction'][prediction_feature]
                for datum in cumulative_data
            ]
            import numpy as np
            counts, binedges = np.histogram(cumulative_feature_data)
            binsize = binedges[1] - binedges[0]
            bin_names = [
                str(round(binedge, 2)) + " : " +
                str(round(binedge + binsize, 2)) for binedge in binedges
            ]
            histogram_graphs_update.append({
                "cumulative_data": {
                    "x": [bin_names],
                    "y": [counts]
                }
            })

        # add updated_at time if not None
        new_time_data_update = [datum['updated_at'] for datum in new_data]
        new_time_data_update_datetime = [
            datetime.fromtimestamp(
                float(t) / 1000).strftime('%Y-%m-%d %H:%M:%S')
            for t in new_time_data_update if t
        ]

        # If feedback not present, add in dummy graph data to add
        if not feedback_features:
            for i in range(num_feedback_features):
                time_series_graphs_extension.append({
                    "new_data": {
                        "x": [[]],
                        "y": [[]],
                    }
                })
                histogram_graphs_update.append({
                    "cumulative_data": {
                        "x": [[]],
                        "y": [[]]
                    }
                })

        for feedback_feature in feedback_features:
            # time series data chart (if not None)
            new_feature_data = [
                datum['feedback'][feedback_feature] for datum in new_data
                if datum['feedback']
            ]
            time_series_graphs_extension.append({
                "new_data": {
                    "x": [new_time_data_update_datetime],
                    "y": [new_feature_data],
                }
            })

            # histogram data chart (if not None)
            cumulative_feature_data = [
                datum['feedback'][feedback_feature]
                for datum in cumulative_data if datum['feedback']
            ]
            import numpy as np
            counts, binedges = np.histogram(cumulative_feature_data)
            binsize = binedges[1] - binedges[0]
            bin_names = [
                str(round(binedge, 2)) + " : " +
                str(round(binedge + binsize, 2)) for binedge in binedges
            ]
            histogram_graphs_update.append({
                "cumulative_data": {
                    "x": [bin_names],
                    "y": [counts]
                }
            })

        for input_feature in input_features:
            # time series data chart
            new_feature_data = [
                datum['input'][input_feature] for datum in new_data
            ]
            time_series_graphs_extension.append({
                "new_data": {
                    "x": [new_time_data_datetime],
                    "y": [new_feature_data],
                }
            })

            # histogram data chart
            cumulative_feature_data = [
                datum['input'][input_feature] for datum in cumulative_data
            ]
            import numpy as np
            counts, binedges = np.histogram(cumulative_feature_data)
            binsize = binedges[1] - binedges[0]
            bin_names = [
                str(round(binedge, 2)) + " : " +
                str(round(binedge + binsize, 2)) for binedge in binedges
            ]
            histogram_graphs_update.append({
                "cumulative_data": {
                    "x": [bin_names],
                    "y": [counts]
                }
            })

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    time_series_graphs_extensionJSON = json.dumps(
        time_series_graphs_extension, cls=plotly.utils.PlotlyJSONEncoder)
    histogram_graphs_updateJSON = json.dumps(
        histogram_graphs_update, cls=plotly.utils.PlotlyJSONEncoder)

    return jsonify(
        time_series_graphs_extension_json_str=time_series_graphs_extensionJSON,
        histogram_graphs_update_json_str=histogram_graphs_updateJSON,
        num_new_results=num_new_results)


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
        "categories": "cool, default",
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
            deployment_info = datmo_monitoring.get_deployment_info(
                deployment_version_id=deployment_version_id)
            deployment_info['deployment_version_id'] = deployment_version_id
            deployment_info['model_version_id'] = model_version_id
            deployments.append(deployment_info)

    # Get the data here (hard coded)
    # TODO: generalize

    # based on the model_version_id and deployment_version_id the user selects
    # show various graphs

    time_series_graphs = []
    histogram_graphs = []

    filter = {
        "model_id": model_id,
        "model_version_id": "model_a",
        "deployment_version_id": "microservice"
    }

    if model_version_ids and deployment_version_ids:
        # filter = {
        #     "model_id": model_id,
        #     "model_version_id": model_version_ids[0],
        #     "deployment_version_id": deployment_version_ids[0]
        # }
        data = datmo_monitoring.search_metadata(filter)
        max_index = 0
        for ind, datum in enumerate(data):
            if datum['feedback'] is not None:
                max_index = ind
        datum = data[max_index]

        def __plotly_graphs(variable_name, time_name="created at"):
            color_choices = [
                "rgb(40,165,187)", "rgb(124,159,57)", "rgb(238,93,134)",
                "rgb(93,147,228)"
            ]
            rand_ind = random.randint(0, 3)
            return ({
                "data": [{
                    "x": [],
                    "y": [],
                    "type": "scatter",
                    "mode": "lines+markers",
                    "marker": {
                        "size": 10,
                        "color": color_choices[rand_ind],
                        "line": {
                            "width": 2,
                            "color": "rgb(80,80,80)"
                        }
                    }
                }],
                "layout": {
                    "title": "time series for " + variable_name,
                    "xaxis": {
                        "title": "time (" + time_name + ")"
                    },
                    "yaxis": {
                        "title": variable_name
                    }
                }
            }, {
                "data": [{
                    "x": [],
                    "y": [],
                    "type": "bar",
                    "marker": {
                        "size": 10,
                        "color": color_choices[rand_ind],
                        "line": {
                            "width": 1.5,
                            "color": "rgb(80,80,80)"
                        }
                    }
                }],
                "layout": {
                    "title": "histogram for " + variable_name,
                    "xaxis": {
                        "title": "buckets"
                    },
                    "yaxis": {
                        "title": "counts"
                    }
                }
            })

        # prediction
        graph_keys = list(datum['prediction'].keys())

        # feedback
        if datum['feedback'] is not None:
            graph_keys.extend(list(datum['feedback'].keys()))

        # input
        graph_keys.extend(list(datum['input'].keys()))

        # add all graphs to the appropriate lists
        for key in graph_keys:
            ts, hist = __plotly_graphs(key)
            time_series_graphs.append(ts)
            histogram_graphs.append(hist)

    # Add "ids" to each of the graphs to pass up to the client
    # for templating
    time_series_ids = [
        'time-series-graph-{}'.format(i)
        for i, _ in enumerate(time_series_graphs)
    ]
    histogram_ids = [
        'histogram-graph-{}'.format(i) for i, _ in enumerate(histogram_graphs)
    ]

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents

    time_series_graphsJSON = json.dumps(
        time_series_graphs, cls=plotly.utils.PlotlyJSONEncoder)
    histogram_graphsJSON = json.dumps(
        histogram_graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template(
        "model_deployments.html",
        user=user,
        model=model,
        deployments=deployments,
        model_version_id=filter['model_version_id'],
        deployment_version_id=filter['deployment_version_id'],
        num_features=len(time_series_graphs),
        time_series_ids=time_series_ids,
        histogram_ids=histogram_ids,
        time_series_graphsJSON=time_series_graphsJSON,
        histogram_graphsJSON=histogram_graphsJSON,
    )


if __name__ == "__main__":
    app.run(debug=True)
