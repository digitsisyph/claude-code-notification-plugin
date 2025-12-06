#!/usr/bin/env python3
"""
Claude Code Notification Hook
=============================
Plays sounds and shows macOS notifications for Claude Code events.

Events: Stop, PermissionRequest, Notification
"""

import copy
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

# Get plugin root directory (supports both plugin install and standalone use)
PLUGIN_ROOT = Path(os.environ.get("CLAUDE_PLUGIN_ROOT", Path(__file__).parent.parent))
CONFIG_FILE = PLUGIN_ROOT / "config.json"
SYSTEM_SOUNDS_DIR = Path("/System/Library/Sounds")

# Default config (used if config.json missing or invalid)
DEFAULT_CONFIG = {
    "sound": True,
    "notification": True,
    "events": {
        "Stop": {"enabled": True, "sound": "Blow"},
        "PermissionRequest": {"enabled": True, "sound": "Funk"},
        "Notification": {"enabled": True, "sound": "Funk"}
    }
}


def load_config():
    """Load config from config.json, fallback to defaults."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                user_config = json.load(f)
                # Merge with defaults (deep copy to avoid mutating DEFAULT_CONFIG)
                config = copy.deepcopy(DEFAULT_CONFIG)
                config["sound"] = user_config.get("sound", config["sound"])
                config["notification"] = user_config.get("notification", config["notification"])
                if "events" in user_config:
                    for event, settings in user_config["events"].items():
                        if event in config["events"]:
                            config["events"][event].update(settings)
                        else:
                            config["events"][event] = settings
                return config
        except Exception:
            pass
    return DEFAULT_CONFIG


def play_sound(sound_name):
    """Play a macOS system sound."""
    if platform.system() != "Darwin":
        return False

    sound_path = SYSTEM_SOUNDS_DIR / f"{sound_name}.aiff"
    if not sound_path.exists():
        return False

    try:
        subprocess.Popen(
            ["afplay", str(sound_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )
        return True
    except Exception:
        return False


def show_notification(title, message):
    """Show macOS notification via terminal-notifier (with osascript fallback)."""
    if platform.system() != "Darwin":
        return False

    # Try terminal-notifier first (more reliable, bypasses Focus Mode)
    try:
        subprocess.run(
            ["terminal-notifier", "-title", title, "-message", message, "-ignoreDnD"],
            check=False, capture_output=True, timeout=5
        )
        return True
    except FileNotFoundError:
        pass
    except Exception:
        pass

    # Fallback to osascript
    try:
        # Escape backslashes first, then double quotes
        escaped_title = title.replace('\\', '\\\\').replace('"', '\\"')
        escaped_message = message.replace('\\', '\\\\').replace('"', '\\"')
        subprocess.run(
            ['osascript', '-e', f'display notification "{escaped_message}" with title "{escaped_title}"'],
            check=False, capture_output=True, timeout=5
        )
        return True
    except Exception:
        return False


def get_notification_message(event_name, hook_data):
    """Build notification message based on event type."""
    if event_name == "Stop":
        return "Task completed"
    elif event_name == "PermissionRequest":
        return get_permission_message(hook_data)
    elif event_name == "Notification":
        return hook_data.get("message", "Alert")[:100]
    return event_name


def get_permission_message(hook_data):
    """Build detailed message for PermissionRequest showing the specific task."""
    tool_name = hook_data.get("tool_name", "")
    tool_input = hook_data.get("tool_input", {})
    description = tool_input.get("description", "")  # Tool description

    if not tool_name:
        return "Permission required"

    def append_desc(msg, max_len=20):
        """Append description if available."""
        if description:
            return f"{msg} ({description[:max_len]})"
        return msg

    if tool_name == "Bash":
        cmd = tool_input.get("command", "")
        if cmd:
            cmd_short = cmd[:30] + "..." if len(cmd) > 30 else cmd
            return append_desc(f"Bash: {cmd_short}")
        return append_desc("Bash command")

    elif tool_name in ("Edit", "Write", "Read"):
        path = tool_input.get("file_path", "")
        if path:
            filename = os.path.basename(path)
            return f"{tool_name}: {filename}"
        return f"{tool_name} file"

    elif tool_name == "Task":
        desc = tool_input.get("description", "")
        if desc:
            return f"Task: {desc[:30]}"
        return "Launch task"

    elif tool_name == "WebFetch":
        url = tool_input.get("url", "")
        if url:
            from urllib.parse import urlparse
            try:
                domain = urlparse(url).netloc
                return f"Fetch: {domain}"
            except Exception:
                pass
        return "Web fetch"

    else:
        return append_desc(tool_name)


def main():
    """Main entry point - reads JSON from stdin."""
    try:
        stdin_content = sys.stdin.read().strip()
        if not stdin_content:
            sys.exit(0)

        hook_data = json.loads(stdin_content)
        event_name = hook_data.get("hook_event_name", "")

        # Load config
        config = load_config()

        # Check if event is enabled
        event_config = config.get("events", {}).get(event_name)
        if not event_config or not event_config.get("enabled", True):
            sys.exit(0)

        # Skip permission_prompt notifications (already handled by PermissionRequest)
        if event_name == "Notification":
            notification_type = hook_data.get("notification_type", "")
            if notification_type == "permission_prompt":
                sys.exit(0)

        # Get folder name for title
        cwd = hook_data.get("cwd", "")
        folder_name = os.path.basename(cwd) if cwd else "Unknown"
        title = f"Claude in {folder_name}"

        # Play sound
        if config.get("sound", True):
            sound_name = event_config.get("sound", "Funk")
            # For Notification events, check for type-specific sound
            if event_name == "Notification":
                notification_type = hook_data.get("notification_type", "")
                types_config = event_config.get("types", {})
                if notification_type and notification_type in types_config:
                    sound_name = types_config[notification_type].get("sound", sound_name)
            play_sound(sound_name)

        # Show notification
        if config.get("notification", True):
            message = get_notification_message(event_name, hook_data)
            show_notification(title, message)

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
