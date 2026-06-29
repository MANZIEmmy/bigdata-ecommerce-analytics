import json
import subprocess


SESSIONS_FILE = "data/sessions_0.json"
TABLE_NAME = "user_sessions"
LIMIT = 100


def safe_value(value):
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value).replace("'", "\\'")
    return str(value).replace("'", "\\'")


def main():
    with open(SESSIONS_FILE, "r", encoding="utf-8") as file:
        sessions = json.load(file)

    commands = []

    for session in sessions[:LIMIT]:
        user_id = session.get("user_id", "")
        session_id = session.get("session_id", "")
        start_time = session.get("start_time", "")
        row_key = f"{user_id}#{start_time}#{session_id}"

        fields = {
            "info:user_id": user_id,
            "info:session_id": session_id,
            "info:start_time": start_time,
            "info:end_time": session.get("end_time", ""),
            "info:duration_seconds": session.get("duration_seconds", ""),
            "device:type": session.get("device_profile", {}).get("type", ""),
            "device:os": session.get("device_profile", {}).get("os", ""),
            "device:browser": session.get("device_profile", {}).get("browser", ""),
            "activity:viewed_products": session.get("viewed_products", []),
            "activity:page_views": session.get("page_views", []),
            "activity:conversion_status": session.get("conversion_status", ""),
            "cart:contents": session.get("cart_contents", {}),
        }

        for column, value in fields.items():
            commands.append(
                f"put '{TABLE_NAME}', '{row_key}', '{column}', '{safe_value(value)}'"
            )

    commands.append("exit")

    process = subprocess.run(
        ["docker", "exec", "-i", "hbase", "hbase", "shell"],
        input="\n".join(commands),
        text=True,
        capture_output=True,
    )

    print(process.stdout)
    print(f"Loaded {LIMIT} sessions into HBase table: {TABLE_NAME}")


if __name__ == "__main__":
    main()