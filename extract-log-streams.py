# one-off script to extract empty, old CloudWatch log files from the output of
# aws --debug logs describe-log-streams --log-group-name LOG_GROUP
# even when the invocation will fail with a ThrottlingException
import re
from json import loads
from json.decoder import JSONDecodeError
from time import time
from datetime import datetime
from typing import Iterable, Union

# only delete logs older than one week
ONLY_TARGET_OLDER_THAN_MS = 3600 * 24 * 7 * 1000
CURRENT_TIME_MS = int(time() * 1000)
ARN_PATTERN = re.compile(r"arn:aws:.*:\d+:log-group:(.*):log-stream:(.*)")


def gen_log_streams(filename: str) -> Iterable[dict[Union[int, str]]]:
    with open(filename, "r") as f:
        for line in f:
            if line.startswith("b'{\"logStreams"):
                try:
                    json_data = loads(line[2:-2])
                except JSONDecodeError as e:
                    raise Exception(line[2:-2], e)

                yield from json_data["logStreams"]


def remove_ineligible(log_stream: dict[str, Union[str, int]]) -> bool:
    if log_stream["storedBytes"] > 0:
        return False
    timestamp = log_stream.get("lastEventTimestamp")
    if not timestamp:
        timestamp = log_stream["creationTime"]
    return timestamp < CURRENT_TIME_MS - ONLY_TARGET_OLDER_THAN_MS


def main():
    log_streams = list(filter(remove_ineligible, gen_log_streams("/tmp/debug")))
    # log_streams = list(gen_log_streams("/tmp/debug"))

    for log_stream in log_streams:
        print(make_command(log_stream))


def make_command(log_stream: dict[str, Union[str, int]]) -> str:
    stream = log_stream["logStreamName"]
    stored_bytes = log_stream["storedBytes"]
    group, _ = ARN_PATTERN.match(log_stream["arn"]).groups()
    created = datetime.fromtimestamp(log_stream["creationTime"] / 1000)
    return (
        f"# Deleting log {stream} with {stored_bytes} stored bytes, created at {created}\n"
        f"aws logs delete-log-stream --log-group-name {group} --log-stream-name {stream}\n"
    )


if __name__ == "__main__":
    main()
