# calstat

A python project for seeing statistics about your time spending based on time allocated to different events on Google Calendar. 

This is NOT finished. Currently it is capable of:
- Printing all events in a certain time-range and certain set of calendars, with information like their title, total time, the calendar they're from, and their label.

## Usage

In order to connect this project to Google Calendar, you need to follow the instructions in the following pages:

[Create a Google Cloud project](https://developers.google.com/workspace/guides/create-project) - Create a project and do NOT enable billing.

[Enable Google Workspace APIs](https://developers.google.com/workspace/guides/enable-apis) - Enable the Google Calendar API in the Google Cloud console website, and do NOT enable any experimental features/enable any other API. Make sure to choose the "Google Calendar API" and not the "CalDAV API".

[Configure the OAuth consent screen and choose scopes](https://developers.google.com/workspace/guides/configure-oauth-consent) - Follow the steps. The branding, user support email, etc. don't matter if you're the only one that's going to be using this project. Select your user type as External (only Google accounts that are part of an organization can choose something else), and add your email as a test user. Add "https://www.googleapis.com/auth/calendar.readonly" as your only scope for this API.

[Create access credentials](https://developers.google.com/workspace/guides/create-credentials#oauth-client-id) - Create OAuth client ID credentials following the steps for a desktop app.


After following these steps, you should be able to run the application. In order to do that, you need to fill data/config.toml with the following information:
- The calendars you want to generate statistics for. For these you need to provide their names. It is important to note that on Google Calendar calendar names are NOT unique. However, I doubt a lot of people have duplicate names, and calendar names are very easy to remember, whereas their IDs aren't. If one of the calendar names you input has 2+ corresponding calendars, the program will throw an error. It will also throw an error if the `Tasks` calendar is inputted, since that works differently. This means you cannot generate statistics for it. It is also important to note that the program only counts `default` type events for its statistics. This is because there's no point in generating statistics for birthdays, and other things like events from Gmail are so different that categorization doesn't really make sense. 
- The date range for which you want to get statistics. This has to be in the format given below, including the timezone.

Example file:
```
calendars = [
    "General", "Exercise", "Hangout", "Rest", "University", "Work"
]
time_min = "2026-07-01T00:00:00+02:00"
time_max = "2026-08-01T00:00:00+02:00"
```

## Development

This project is managed with Pixi, using Hatchling as its Python build backend, pytest for tests, and Ruff for linting and formatting.

Make sure to install Pixi before working on the project. In terms of the code editor, I use VSCode, and I have some useful settings for it in the repository. I also used the following extensions:

| Extension | ID | Purpose |
|---|---|---|
| Python | `ms-python.python` | Python editing, debugging, testing, and environment integration |
| Pylance | `ms-python.vscode-pylance` | Type analysis, hover information, navigation, and auto-imports |
| Python Environments | `ms-python.vscode-python-envs` | Environment discovery and selection |
| Pixi Code | `renan-r-santos.pixi-code` | Connects Pixi environments to VS Code's Python environment system |
| Ruff | `charliermarsh.ruff` | Ruff diagnostics, fixes, and formatting |
| Google Workspace Developer Tools | `google-workspace` | OAuth2 Scope Linting |

To start writing code, clone the repository using git, and install the environment using:

```bash
pixi install
```

Run the application through the named Pixi task:

```bash
pixi run run
```

Other commands you may need for development are defined in `pyproject.toml` under `tool.pixi.tasks`.