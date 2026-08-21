import logging

logger = logging.getLogger(__name__)


def _scrub_frame_vars(frame_vars, lookup_objects):
    for var in frame_vars:
        if var in lookup_objects:
            frame_vars[var] = "Scrubbed"
        for val in (values := frame_vars.get("values", [])):
            if val in lookup_objects:
                values[val] = "Scrubbed"


def sentry_scrubber(*args, **kwargs):
    event = args[0]

    if not event:
        return

    # Objection are stored in stacktrace and might contain sensitive data, and we want
    # it to be scrubbed.
    lookup_objects = [
        "objection",
        "sanitised_objection",
        "objection_without_attachment_data",
    ]
    try:
        for value in event.get("exception", {}).get("values", []):
            for frame in value.get("stacktrace", {}).get("frames", []):
                _scrub_frame_vars(frame.get("vars", []), lookup_objects)
    except BaseException as e:  # noqa
        logger.warning("Failed to scrub objection data", exc_info=e)

    return event
