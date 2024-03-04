import logging


def stringToBool(strBool: str, default: bool):
    if strBool.lower() == "true":
        return True
    if strBool.lower() == "false":
        return False
    return default


def sentry_scrubber(*args, **kwargs):
    event = args[0]

    if not event:
        return

    # Objection are stored in stacktrace and might contain sensitive data, and we want it to be scrubbed.
    lookup_objects = [
        "objection",
        "sanitised_objection",
        "objection_without_attachment_data",
    ]
    try:
        for value in event.get("exception", {}).get("values", []):
            for frame in value.get("stacktrace", {}).get("frames", []):
                for var in (frame_vars := frame.get("vars", [])):
                    if var in lookup_objects:
                        frame_vars[var] = "Scrubbed"
                    for val in (values := frame_vars.get("values", [])):
                        if val in lookup_objects:
                            values[val] = "Scrubbed"
    except BaseException as e:  # noqa
        logging.warning("Failed to scrub objection data", exc_info=e)

    return event
