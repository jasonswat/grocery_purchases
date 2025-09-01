# Grocery Purchases
Python app to pull grocery purchase history. Currently setup for kroger, but hoping to add additional grocers that make purchase history available online.

## Setup python environment:

1. Create virtual python environment, depending on which you use:

create pyenv virtual environment and activate:
```bash
pyenv virtualenv 3.12.2 kroger312
pyenv activate kroger312
```

create miniconda virtual environment and activate:
```bash
conda create -n kroger312 python=3.12
conda activate kroger312
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Setup Credentials
setup environment variables for your kroger account:
```bash
export KROGER_USERNAME="your_username"
export KROGER_PASSWORD="your_password"
```
## Avoid detection

The script is pulling data for a single account which I own, but because I'm using playwright to automate it, the site is detecting it as a bot and blocking it. I believe Kroger is using Akamai for detecting bots.

To avoid detection I added the following:

1. Added a random user agent with fake_useragent
2. Added browser settings for chromium and tested at https://bot.sannysoft.com/.
3. You can run `python test_browser_settings.py` to test that is passes bot.sannysoft detection.

Application firewalls are constantly updating their detection methods, so this may not work for long.

See links below in the resources section for more info on avoiding detection.

## Enable Debugging

```bash
export DEBUG=pw:api,pw:browser
```

## Resources
 * https://www.youtube.com/watch?v=H2-5ecFwHHQ
 * https://github.com/Shmakov/kroger-cli
 * https://github.com/agg23/kroger/blob/7f680a5aa7aaf6088c7d577c6d7db35c013b3d4f/index.ts#L28 
 * Haven't looked at this too much, but putting it here in case: https://github.com/ThermoMan/Get-Kroger-Grocery-List/blob/main/Get%20Kroger%20Grocery%20List.user.js

#### bot detection related
 * https://scrapeops.io/playwright-web-scraping-playbook/nodejs-playwright-make-playwright-undetectable/
 * https://scrapingant.com/blog/web-scraping-playwright-python-part-4 
 * playwright replacement (haven't tried) https://github.com/Kaliiiiiiiiii-Vinyzu/patchright
