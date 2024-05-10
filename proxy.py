import os


def proxies(username: str, password: str, endpoint: str, port: str, kw: str = "") -> str:
    """Used to make an extension to connect to a proxy"""

    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Proxies",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        },
        "minimum_chrome_version":"22.0.0"
    }
    """

    background_js = """
    var config = {
            mode: "fixed_servers",
            rules: {
              singleProxy: {
                scheme: "http",
                host: "%s",
                port: parseInt(%s)
              },
              bypassList: ["localhost"]
            }
          };

    chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});

    function callbackFn(details) {
        return {
            authCredentials: {
                username: "%s",
                password: "%s"
            }
        };
    }

    chrome.webRequest.onAuthRequired.addListener(
                callbackFn,
                {urls: ["<all_urls>"]},
                ['blocking']
    );
    """ % (
        endpoint,
        port,
        username,
        password,
    )

    folder_path = os.path.join(f"{os.getcwd()}/extensions/proxy{kw}")
    os.makedirs(folder_path, exist_ok=True)
    with open(os.path.join(folder_path, "manifest.json"), "w") as fp:
        fp.write(manifest_json)
    with open(os.path.join(folder_path, "background.js"), "w") as fp:
        fp.write(background_js)

    return folder_path
