# Claude Code Notification

[中文文档](README_CN.md)

A minimal Claude Code plugin that adds sound and notification alerts on macOS.

Get notified when Claude Code completes a task or needs your permission.

![Notification Demo](assets/notification-demo.png)

## Features

- **Sound alerts** - plays macOS system sounds
- **Desktop notifications** - shows macOS notifications (works even in Focus Mode)
- **Easy installation** - install directly from GitHub as a Claude Code plugin
- **Configurable** - customize sounds, enable/disable events

## Installation

### Prerequisites (recommended)

```bash
brew install terminal-notifier
```

### Install Plugin

In Claude Code, run:

```
/plugin marketplace add digitsisyph/claude-code-notification-plugin
/plugin install claude-code-notification
```

## Uninstallation

```
/plugin uninstall claude-code-notification
```

## Update

```
/plugin update claude-code-notification
```

## Customization

After installation, edit `config.json` in the plugin directory for Customization:

```json
{
  "sound": true,
  "notification": true,
  "events": {
    "Stop": {
      "enabled": true,
      "sound": "Blow",
      "emoji": "✅"
    },
    "PermissionRequest": {
      "enabled": true,
      "sound": "Funk",
      "emoji": "🔐"
    },
    "Notification": {
      "enabled": true,
      "sound": "Funk",
      "emoji": "💬",
      "types": {
        "error": { "sound": "Sosumi", "emoji": "❌" },
        "warning": { "sound": "Sosumi", "emoji": "⚠️" },
        "success": { "sound": "Glass", "emoji": "✅" }
      }
    }
  }
}
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `sound` | Enable/disable all sounds | `true` |
| `notification` | Enable/disable all notifications | `true` |
| `events.*.enabled` | Enable/disable specific event | `true` |
| `events.*.sound` | Sound for specific event | varies |
| `events.*.emoji` | Emoji prefix in notification title | varies |
| `events.Notification.types` | Type-specific sounds and emojis | optional |

### Available Sounds

Any `.aiff` file in `/System/Library/Sounds/`:

`Basso`, `Blow`, `Bottle`, `Frog`, `Funk`, `Glass`, `Hero`, `Morse`, `Ping`, `Pop`, `Purr`, `Sosumi`, `Submarine`, `Tink`

## Events

| Event | Description |
|-------|-------------|
| `Stop` | Claude completed a task |
| `PermissionRequest` | Claude needs your permission |
| `Notification` | Claude sent a notification |

## Requirements

- macOS
- Python 3 (pre-installed on macOS)
- [terminal-notifier](https://github.com/julienXX/terminal-notifier) (recommended, for Focus Mode bypass)

## How It Works

This plugin uses [Claude Code hooks](https://code.claude.com/docs/en/hooks) to trigger a Python script when specific events occur. The script plays a system sound and shows a notification.

## Inspiration

This project was inspired by:

- [wyattjoh/claude-code-notification](https://github.com/wyattjoh/claude-code-notification)
- [Using terminal-notifier for Claude Code custom notifications](https://www.andreagrandi.it/posts/using-terminal-notifier-claude-code-custom-notifications/) by Andrea Grandi

## License

MIT
