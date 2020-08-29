from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, url_for
from flask_login import current_user, login_required
from ..helper import (
    admin_required,
    build_callback_url,
    build_topic_url,
)
from ..models import Channel
from ..tasks import renew_channels

api_channel_blueprint = Blueprint("api_channel", __name__)


@api_channel_blueprint.route("/renew-all")
@login_required
def renew_all():
    """Renew Subscription Info, Both Hub and Info"""
    next_countdown = int(request.args.to_dict().get("next_countdown", -1))
    immediate = bool(next_countdown <= 0)
    compact_args = []
    response = {}
    for channel in Channel.query.all():
        task_args = (
            channel.id,
            build_callback_url(channel.id),
            build_topic_url(channel.id),
        )
        if immediate:
            compact_args.append(task_args)
        else:
            expiration = channel.expiration
            if expiration is not None:
                eta = channel.expiration - timedelta(days=1)
            else:
                eta = datetime.now() + timedelta(days=4)
            task = renew_channels.apply_async(
                args=[[task_args], next_countdown],
                eta=eta,
                task_id=f"renew_{channel.id}",
            )
            response[channel.id] = task.id
    if immediate:
        task = renew_channels.apply_async(args=[compact_args])
        response = {
            "id": task.id,
            "status": url_for("api_task.status", task_id=task.id),
        }
    return jsonify(response)


@api_channel_blueprint.route("/<channel_id>/status")
@login_required
def status(channel_id):
    """From Hub fetch Status"""
    channel = Channel.query.filter_by(id=channel_id).first_or_404()
    response = channel.update_hub_infos()
    return jsonify(response)


@api_channel_blueprint.route("/<channel_id>/subscribe")
@login_required
def subscribe(channel_id):
    """Subscribe to a Channel"""
    return jsonify(current_user.subscribe_to(channel_id))


@api_channel_blueprint.route("/<channel_id>/unsubscribe")
@login_required
def unsubscribe(channel_id):
    """Unsubscribe to a Channel"""
    return jsonify(current_user.unbsubscribe(channel_id))


@api_channel_blueprint.route("/<channel_id>/renew")
@login_required
def renew(channel_id):
    """Renew Subscription Info, Both Hub and Info"""
    channel = Channel.query.filter_by(id=channel_id).first_or_404()
    response = channel.renew(stringify=True)
    return jsonify(response)


@api_channel_blueprint.route("/<channel_id>/fetch-videos")
@login_required
@admin_required
def fetch_videos(channel_id):
    # TODO: deprecate this
    channel_item = Channel.query.filter_by(id=channel_id).first_or_404()
    response = channel_item.fetch_videos()
    return jsonify(response)