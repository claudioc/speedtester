# Speedtester

Runs a network speedtest (using [speedtest-cli](https://github.com/sivel/speedtest-cli)) and appends the results in a Google Spreadsheet of your choice.

The information saved in the spreadsheet are:

- timestamp
- the ping latency
- download speed (in MB/s)
- upload speed (in MB/s)
- Internet service provider name

## Why Speedtester?

I needed a way to automatically track the speedtest of my home connection
over time and I think that using a script and a Google Spreadsheet as the
database may be the simplest solution.

## Requirements

1.  Download or clone this repository in its own directory
2.  Install the required packages with `pip install --upgrade speedtest-cli python-dotenv google-api-python-client google-auth-httplib2 google-auth-oauthlib`
3.  Create a new [Google Cloud Platform project](https://cloud.google.com/appengine/docs/standard/nodejs/building-app/creating-project) and enable the Google Sheets API and get its Google Client Id and Google Client Secret. You can quickly use the option in the [Step 1](https://developers.google.com/sheets/api/quickstart/python) of the API quickstart tutorial for this task
4.  Create a [Google Spreadsheet](https://sheet.new). Leave it completely empty, the script will fill it up with the headers cells as well
5.  Copy the provided `.env.example` in `.env` and fill it in with the configuration values

On the very first run the script will open the browser so that Google will ask for confirmation of the access request and allow the creation of the OAuth and refresh token. The information is then locally saved in the `token.pickle` file and never asked again.

If eveything runs as expected, the idea is then to run the script from a crontab on a computer always connected to your internet connection.

## More about the test runner

The "default" speed test runner is https://github.com/sivel/speedtest-cli but you can use the binary [CLI from Speedtest](https://www.speedtest.net/apps/cli).

That CLI is a big slower, a bit more accurate and has the `packetLoss` statistic, missing from the default one.

When using Speedtest CLI you need to change the source a bit; run it with:

```
  result = subprocess.run(['speedtest', '-f', 'json', '-p', 'no'], stdout=subprocess.PIPE)
  test_result = json.loads(result.stdout)

  'values': [
      [
          test_result['timestamp'],
          test_result['ping']['latency'],
          test_result['download']['bandwidth'],
          test_result['upload']['bandwidth'],
          test_result['packetLoss'],
          test_result['isp']
      ]
  ]
```

# References

- [Google Sheets API](https://developers.google.com/sheets/api/guides/concepts)
