from __future__ import print_function

import os
from datetime import datetime

from datmo.core.util.i18n import get as __
from datmo.cli.driver.helper import Helper
from datmo.core.util.misc_functions import mutually_exclusive, printable_object, prettify_datetime, parse_cli_key_value, format_table
from datmo.core.util.exceptions import (SnapshotCreateFromTaskArgs)
from datmo.cli.command.project import ProjectCommand
from datmo.core.controller.snapshot import SnapshotController


class SnapshotCommand(ProjectCommand):
    def __init__(self, cli_helper):
        super(SnapshotCommand, self).__init__(cli_helper)

    def usage(self):
        self.cli_helper.echo(__("argparser", "cli.snapshot.usage"))

    def snapshot(self):
        self.parse(["snapshot", "--help"])
        return True

    @Helper.notify_no_project_found
    def create(self, **kwargs):
        self.snapshot_controller = SnapshotController()
        self.cli_helper.echo(__("info", "cli.snapshot.create"))
        run_id = kwargs.get("run_id", None)
        # creating snapshot with task id if it exists
        if run_id is not None:
            excluded_args = [
                "environment_id", "environment_paths", "paths",
                "config_filepath", "config_filename", "stats_filepath",
                "stats_filename"
            ]
            for arg in excluded_args:
                if arg in kwargs and kwargs[arg] is not None:
                    raise SnapshotCreateFromTaskArgs(
                        "error", "cli.snapshot.create.run.args", arg)

            message = kwargs.get("message", None)
            label = kwargs.get("label", None)
            # Create a new core snapshot object
            snapshot_task_obj = self.snapshot_controller.create_from_task(
                message, run_id, label=label)
            self.cli_helper.echo(
                "Created snapshot id: %s" % snapshot_task_obj.id)
            return snapshot_task_obj
        else:
            # creating snapshot without task id
            snapshot_dict = {"visible": True}

            # Environment
            if kwargs.get("environment_id", None) or kwargs.get(
                    "environment_paths", None):
                mutually_exclusive_args = [
                    "environment_id", "environment_paths"
                ]
                mutually_exclusive(mutually_exclusive_args, kwargs,
                                   snapshot_dict)

            # File
            if kwargs.get("paths", None):
                snapshot_dict['paths'] = kwargs['paths']

            # Config
            if kwargs.get("config_filepath", None) or kwargs.get(
                    "config_filename", None) or kwargs.get("config", None):
                mutually_exclusive_args = [
                    "config_filepath", "config_filename", "config"
                ]
                mutually_exclusive(mutually_exclusive_args, kwargs,
                                   snapshot_dict)
            # parsing config
            if "config" in snapshot_dict:
                config = {}
                config_list = snapshot_dict["config"]
                for item in config_list:
                    item_parsed_dict = parse_cli_key_value(item, 'config')
                    config.update(item_parsed_dict)
                snapshot_dict["config"] = config

            # Stats
            if kwargs.get("stats_filepath", None) or kwargs.get(
                    "stats_filename", None) or kwargs.get("config", None):
                mutually_exclusive_args = [
                    "stats_filepath", "stats_filename", "stats"
                ]
                mutually_exclusive(mutually_exclusive_args, kwargs,
                                   snapshot_dict)
            # parsing stats
            if "stats" in snapshot_dict:
                stats = {}
                stats_list = snapshot_dict["stats"]
                for item in stats_list:
                    item_parsed_dict = parse_cli_key_value(item, 'stats')
                    stats.update(item_parsed_dict)
                snapshot_dict["stats"] = stats

            optional_args = ["session_id", "message", "label"]

            for arg in optional_args:
                if arg in kwargs and kwargs[arg] is not None:
                    snapshot_dict[arg] = kwargs[arg]

            snapshot_obj = self.snapshot_controller.create(snapshot_dict)
            # Because snapshots may be invisible to the user, this function ensures that by the end
            # the user can monitor the snapshot on the CLI, but making it visible
            snapshot_obj = self.snapshot_controller.update(
                snapshot_obj.id, visible=True)
            self.cli_helper.echo(
                __("info", "cli.snapshot.create.success", snapshot_obj.id))
            return snapshot_obj

    @Helper.notify_no_project_found
    def delete(self, **kwargs):
        self.snapshot_controller = SnapshotController()
        self.cli_helper.echo(__("info", "cli.snapshot.delete"))
        snapshot_id = kwargs.get('id')
        result = self.snapshot_controller.delete(snapshot_id)
        self.cli_helper.echo(
            __("info", "cli.snapshot.delete.success", snapshot_id))
        return result

    @Helper.notify_no_project_found
    def update(self, **kwargs):
        self.snapshot_controller = SnapshotController()
        self.cli_helper.echo(__("info", "cli.snapshot.update"))
        snapshot_id = kwargs.get('id')
        # getting previous saved config and stats
        snapshot_obj = self.snapshot_controller.get(snapshot_id)
        config = snapshot_obj.config
        stats = snapshot_obj.stats

        # extracting config
        update_config_list = kwargs.get('config', None)
        if update_config_list:
            update_config = {}
            for item in update_config_list:
                item_parsed_dict = parse_cli_key_value(item, 'config')
                update_config.update(item_parsed_dict)
            # updating config
            config.update(update_config)

        # extracting stats
        update_stats_list = kwargs.get('stats', None)
        if update_stats_list:
            update_stats = {}
            for item in update_stats_list:
                item_parsed_dict = parse_cli_key_value(item, 'stats')
                update_stats.update(item_parsed_dict)
            # updating stats
            stats.update(update_stats)

        # extracting message
        message = kwargs.get('message', None)
        # extracting label
        label = kwargs.get('label', None)

        result = self.snapshot_controller.update(
            snapshot_id,
            config=config,
            stats=stats,
            message=message,
            label=label)
        self.cli_helper.echo(
            __("info", "cli.snapshot.update.success", snapshot_id))
        return result

    @Helper.notify_no_project_found
    def ls(self, **kwargs):
        self.snapshot_controller = SnapshotController()
        session_id = kwargs.get('session_id',
                                self.snapshot_controller.current_session.id)
        detailed_info = kwargs.get('details', None)
        show_all = kwargs.get('show_all', None)
        print_format = kwargs.get('format', "table")
        download = kwargs.get('download', None)
        download_path = kwargs.get('download_path', None)
        current_snapshot_obj = self.snapshot_controller.current_snapshot()
        current_snapshot_id = current_snapshot_obj.id if current_snapshot_obj else None
        if show_all:
            snapshot_objs = self.snapshot_controller.list(
                session_id=session_id,
                sort_key="created_at",
                sort_order="descending")
        else:
            snapshot_objs = self.snapshot_controller.list(
                session_id=session_id,
                visible=True,
                sort_key="created_at",
                sort_order="descending")
        item_dict_list = []
        if detailed_info:
            header_list = [
                "id", "created at", "config", "stats", "message", "label",
                "code id", "environment id", "file collection id"
            ]
            for snapshot_obj in snapshot_objs:
                snapshot_config_printable = printable_object(
                    snapshot_obj.config)
                snapshot_stats_printable = printable_object(snapshot_obj.stats)
                snapshot_message = printable_object(snapshot_obj.message)
                snapshot_label = printable_object(snapshot_obj.label)
                printable_snapshot_id = snapshot_obj.id if current_snapshot_id is not None and \
                                                           snapshot_obj.id != current_snapshot_id\
                    else "(current) " + snapshot_obj.id
                item_dict_list.append({
                    "id": printable_snapshot_id,
                    "created at": prettify_datetime(snapshot_obj.created_at),
                    "config": snapshot_config_printable,
                    "stats": snapshot_stats_printable,
                    "message": snapshot_message,
                    "label": snapshot_label,
                    "code id": snapshot_obj.code_id,
                    "environment id": snapshot_obj.environment_id,
                    "file collection id": snapshot_obj.file_collection_id
                })
        else:
            header_list = [
                "id", "created at", "config", "stats", "message", "label"
            ]
            for snapshot_obj in snapshot_objs:
                snapshot_config_printable = printable_object(
                    snapshot_obj.config)
                snapshot_stats_printable = printable_object(snapshot_obj.stats)
                snapshot_message = printable_object(snapshot_obj.message)
                snapshot_label = printable_object(snapshot_obj.label)
                printable_snapshot_id = snapshot_obj.id if current_snapshot_id is not None and \
                                                           snapshot_obj.id != current_snapshot_id \
                    else "(current) " + snapshot_obj.id
                item_dict_list.append({
                    "id": printable_snapshot_id,
                    "created at": prettify_datetime(snapshot_obj.created_at),
                    "config": snapshot_config_printable,
                    "stats": snapshot_stats_printable,
                    "message": snapshot_message,
                    "label": snapshot_label,
                })
        if download:
            if not download_path:
                # download to current working directory with timestamp
                current_time = datetime.utcnow()
                epoch_time = datetime.utcfromtimestamp(0)
                current_time_unix_time_ms = (
                    current_time - epoch_time).total_seconds() * 1000.0
                download_path = os.path.join(
                    self.snapshot_controller.home,
                    "snapshot_ls_" + str(current_time_unix_time_ms))
            self.cli_helper.print_items(
                header_list,
                item_dict_list,
                print_format=print_format,
                output_path=download_path)
            return snapshot_objs
        self.cli_helper.print_items(
            header_list, item_dict_list, print_format=print_format)
        return snapshot_objs

    @Helper.notify_no_project_found
    def checkout(self, **kwargs):
        self.snapshot_controller = SnapshotController()
        snapshot_id = kwargs.get('id')
        checkout_success = self.snapshot_controller.checkout(snapshot_id)
        if checkout_success:
            self.cli_helper.echo(
                __("info", "cli.snapshot.checkout.success", snapshot_id))
        return self.snapshot_controller.checkout(snapshot_id)

    @Helper.notify_no_project_found
    def diff(self, **kwargs):
        self.snapshot_controller = SnapshotController()
        snapshot_id_1 = kwargs.get("id_1", None)
        snapshot_id_2 = kwargs.get("id_2", None)
        snapshot_obj_1 = self.snapshot_controller.get(snapshot_id_1)
        snapshot_obj_2 = self.snapshot_controller.get(snapshot_id_2)
        comparison_attributes = [
            "id", "created_at", "message", "label", "code_id",
            "environment_id", "file_collection_id", "config", "stats"
        ]
        table_data = [["Attributes", "Snapshot 1", "", "Snapshot 2"],
                      ["", "", "", ""]]
        for attribute in comparison_attributes:
            value_1 = getattr(snapshot_obj_1, attribute) if getattr(
                snapshot_obj_1, attribute) else "N/A"
            value_2 = getattr(snapshot_obj_2, attribute) if getattr(
                snapshot_obj_2, attribute) else "N/A"
            if isinstance(value_1, datetime):
                value_1 = prettify_datetime(value_1)
            if isinstance(value_2, datetime):
                value_2 = prettify_datetime(value_2)
            if attribute in ["config", "stats"]:
                alldict = []
                if isinstance(value_1, dict): alldict.append(value_1)
                if isinstance(value_2, dict): alldict.append(value_2)
                allkey = set().union(*alldict)
                for key in allkey:
                    key_value_1 = "%s: %s" % (key, value_1[key]) if value_1 != "N/A" and value_1.get(key, None) \
                        else "N/A"
                    key_value_2 = "%s: %s" % (key, value_2[key]) if value_2 != "N/A" and value_2.get(key, None) \
                        else "N/A"
                    table_data.append(
                        [attribute, key_value_1, "->", key_value_2])
            else:
                table_data.append([attribute, value_1, "->", value_2])
        output = format_table(table_data)
        self.cli_helper.echo(output)
        return output

    @Helper.notify_no_project_found
    def inspect(self, **kwargs):
        self.snapshot_controller = SnapshotController()
        snapshot_id = kwargs.get("id", None)
        snapshot_obj = self.snapshot_controller.get(snapshot_id)
        output = str(snapshot_obj)
        self.cli_helper.echo(output)
        return output
