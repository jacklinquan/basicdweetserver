# basicdweetserver

Basic dweet server with [FastAPI] and [Deta].

## The `basicdweetserver` app

- Create a directory for the app, for example, `./basicdweetserver/` and enter into it.

### FastAPI code

- Create a `main.py` file.

### Requirements

- In the same directory create a `requirements.txt` file.

### Directory structure

You will now have one directory `./basicdweetserver/` with two files:

```
.
└── main.py
└── requirements.txt
```

## Create a free Deta account

Now create a free account on [Deta], you just need an email and password.

## Install the CLI

Once you have your account, install the Deta CLI:

- On `Linux` or `macOS`:

```console
$ curl -fsSL https://get.deta.dev/cli.sh | sh
```

- On `Windows` in `PowerShell`:

```console
> iwr https://get.deta.dev/cli.ps1 -useb | iex
```

After installing it, open a new terminal so that the installed CLI is detected.

## Login with the CLI

Now login to Deta from the CLI with:

```console
$ deta login

Please, log in from the web page. Waiting..
Logged in successfully.
```

This will open a web browser and authenticate automatically.

## Deploy with Deta

Next, deploy your application with the Deta CLI:

```console
$ deta new

Successfully created a new micro
{
        "name": "basicdweetserver",
        "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        "project": "xxxxxxxx",
        "runtime": "python3.9",
        "endpoint": "https://xxxxxx.deta.dev",
        "region": "ap-southeast-1",
        "visor": "disabled",
        "http_auth": "disabled"
}
Adding dependencies...
...
Successfully installed...
```

> **Note:**
> 
> Your deployment will have a different `"endpoint"` URL.

For existing apps, deploy with the Deta CLI:

```console
$ deta deploy
```

## Enable public access

You can make it public with:

```console
$ deta auth disable

Successfully disabled http auth
```

Now you can share that URL with anyone and they will be able to access your API.

## Check it

Now open your browser in your `endpoint` URL. In the example above it was `https://xxxxxx.deta.dev`, but yours will be different.

You will see the JSON response from your FastAPI app:

```json
{
  "Description": "Basic dweet server.",
  "/dweet/for/{thing}": "Create a dweet for a thing.",
  "/get/latest/dweet/for/{thing}": "Read the latest dweet for a thing.",
  "/get/dweets/for/{thing}": "Read the last 5 cached dweets for a thing."
}
```

And you can also go to the `/docs` for your API, in the example above it would be `https://xxxxxx.deta.dev/docs`.

## Use the API with `basicdweet`

### Install `basicdweet`

```console
$ pip install basicdweet
```

### Use `basicdweet`

```python
>>> import basicdweet
>>> base_url = 'https://xxxxxx.deta.dev'
>>> basicdweet.dweet_for('YOUR_THING', {'YOUR_DATA': 'YOUR_VALUE'}, base_url=base_url)
{'content': {'YOUR_DATA': 'YOUR_VALUE'}, 'created': '2022-05-27T06:17:48.127Z', 'thing': 'YOUR_THING', 'transaction': '403dcd2b-99b9-44b4-b864-b682b898ac10'}
>>> basicdweet.get_latest_dweet_for('YOUR_THING', base_url=base_url)
[{'content': {'YOUR_DATA': 'YOUR_VALUE'}, 'created': '2022-05-27T06:17:48.127Z', 'thing': 'YOUR_THING'}]
>>> basicdweet.dweet_for('YOUR_THING', {'YOUR_DATA': 'YOUR_VALUE_2'}, base_url=base_url)
{'content': {'YOUR_DATA': 'YOUR_VALUE_2'}, 'created': '2022-05-27T06:19:08.081Z', 'thing': 'YOUR_THING', 'transaction': '30cdc5b8-5da9-40ac-86a9-ea0df5ef8317'}
>>> basicdweet.get_latest_dweet_for('YOUR_THING', base_url=base_url)
[{'content': {'YOUR_DATA': 'YOUR_VALUE_2'}, 'created': '2022-05-27T06:19:08.081Z', 'thing': 'YOUR_THING'}]
>>> basicdweet.get_dweets_for('YOUR_THING', base_url=base_url)
[{'content': {'YOUR_DATA': 'YOUR_VALUE_2'}, 'created': '2022-05-27T06:19:08.081Z', 'thing': 'YOUR_THING'}, {'content': {'YOUR_DATA': 'YOUR_VALUE'}, 'created': '2022-05-27T06:17:48.127Z', 'thing': 'YOUR_THING'}]
```

## Use the API with `basicdweet` and API key

### Disable public access

You can make it private with:

```console
$ deta auth enable
```

### Create an API key

To create a new API key, run the following command, make sure to provide at least the `name` argument:

```console
$ deta auth create-api-key --name basicdweetserver_api_key --desc "API key for basicdweetserver"
```

This will send a response similar to this:

```json
{
    "name": "basicdweetserver_api_key",
    "description": "API key for basicdweetserver",
    "prefix": "randomprefix",
    "api_key": "randomprefix.supersecretrandomstring",
    "created": "2022-09-01T20:50:15Z"
}
```

In this example, the API key would be `randomprefix.supersecretrandomstring`.
The key will only be shown to you once, make sure to save it in a secure place.

### Use `basicdweet` with API key

```python
>>> import basicdweet
>>> base_url = 'https://xxxxxx.deta.dev'
>>> api_key = 'randomprefix.supersecretrandomstring'
>>> basicdweet.dweet_for('YOUR_THING', {'YOUR_DATA': 'YOUR_VALUE'}, base_url=base_url, headers={"X-API-Key": api_key})
{'content': {'YOUR_DATA': 'YOUR_VALUE'}, 'created': '2022-05-27T06:17:48.127Z', 'thing': 'YOUR_THING', 'transaction': '403dcd2b-99b9-44b4-b864-b682b898ac10'}
>>> basicdweet.get_latest_dweet_for('YOUR_THING', base_url=base_url, headers={"X-API-Key": api_key})
[{'content': {'YOUR_DATA': 'YOUR_VALUE'}, 'created': '2022-05-27T06:17:48.127Z', 'thing': 'YOUR_THING'}]
>>> basicdweet.dweet_for('YOUR_THING', {'YOUR_DATA': 'YOUR_VALUE_2'}, base_url=base_url, headers={"X-API-Key": api_key})
{'content': {'YOUR_DATA': 'YOUR_VALUE_2'}, 'created': '2022-05-27T06:19:08.081Z', 'thing': 'YOUR_THING', 'transaction': '30cdc5b8-5da9-40ac-86a9-ea0df5ef8317'}
>>> basicdweet.get_latest_dweet_for('YOUR_THING', base_url=base_url, headers={"X-API-Key": api_key})
[{'content': {'YOUR_DATA': 'YOUR_VALUE_2'}, 'created': '2022-05-27T06:19:08.081Z', 'thing': 'YOUR_THING'}]
>>> basicdweet.get_dweets_for('YOUR_THING', base_url=base_url, headers={"X-API-Key": api_key})
[{'content': {'YOUR_DATA': 'YOUR_VALUE_2'}, 'created': '2022-05-27T06:19:08.081Z', 'thing': 'YOUR_THING'}, {'content': {'YOUR_DATA': 'YOUR_VALUE'}, 'created': '2022-05-27T06:17:48.127Z', 'thing': 'YOUR_THING'}]
```

[FastAPI]: https://fastapi.tiangolo.com/
[Deta]: https://www.deta.sh/
