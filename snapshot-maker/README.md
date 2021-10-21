# Snapshot Maker - Function Compute Example

- Status: **OK**
- Notes: Code tested and working as of 2021-10-21 (YYYY-MM-DD)

## What Does The Code Do?

The function compute code in the `fc-function` folder sets up an HTTP-triggered function that can make ECS disk snapshots.

When you send a GET or POST request to the HTTP trigger with the `?diskID=` parameter set to a valid disk ID, the function will make a snapshot of said disk.

The function is written in Python3, and (for simplicity) hard-codes an Access Key and Region. In a real world scenario, you might want to add additional parameters such as:

- Snapshot name
- Region
- Tags (to attack to the snapshot)

...and so on. 

Please **do not use this code in production**. In a real-world scenario, you do **not** want to hard-code your access credentials into your functions. Instead, you should be creating RAM roles [as described here](https://www.alibabacloud.com/help/doc-detail/181589.htm). Your FC functions can then use `AssumeRole` to get temporary credentials, as needed. 

## Initial Setup

Before you get started, you should install the Alibaba Cloud function compute command line tool, `fun`. You may also want to install Docker, if you plan to test functions locally before deploying them to Alibaba Cloud.

- Information on installing Docker is [here](https://docs.docker.com/get-docker/)
- Installation instructions for `fun` are [here](https://www.alibabacloud.com/help/doc-detail/161136.htm)

Note that the `fun` command line tool is **distributed using NPM** so you'll need to have `npm` installed in order to install fun. If you are on a Mac, you might want to consider installing `npm` through [Homebrew](https://brew.sh/), a handy Mac package manager.

After you install `fun` you need to run `fun configure` and enter your Alibaba Cloud Account ID, Access Key, Access Key Secret, and the default Alibaba Cloud Region (this is where `fun` will deploy functions when you run `fun deploy`). Details on configuring `fun` can be found on [this page](https://www.alibabacloud.com/help/doc-detail/146702.htm). 

## Updating The Function

Before we deploy our code, we need to change the *GLOBALS* section inside `index.py` so that it includes a real AccessKey, AccessKey Secret, and Region name, like so:

```
###########
# GLOBALS #
###########
access_key = "LTAI5tSArY9Zgi41tbGGovQe"
secret = "4KJY6vQ3RGc4rn8KDOGSWT4xm9iz9N"
region = "ap-southeast-1"
```

After you have made this change, save `index.py` and move on to the next step. 

## Deploying The Function

Our function doesn't include any custom libraries or extra dependencies, so we can skip `fun build` and go straight to `fun deploy`. 

Simply `cd` into the fc-function directory and run `fun deploy`. 

That's it! See the section below to learn how to generate valid URI strings to actually call the new FC function via `curl` or your favorite web browser.

### Testing it out

One of the outputs returned by `fun deploy` is the URL endpoint of our new Function Compute function. Plugging this URL into the `curl` command or a web browser, and appending `?diskID=` at the end will let us make a snapshot of any disk. For instance, we might try:

```
curl "http://my-fc-endpoint?diskID=d-t4ng5a4ia2jn5memzlv3"
```

This should return a message similar to this one:

```
{
   "SnapshotId": "s-t4n16lk2h2yqs3mmld87",
   "RequestId": "BBDFA814-5F3D-32F6-8B58-1CEE3437B97B"
}
```

If you get a response like the one above with a Request ID and Snapshot ID, then the snapshot creation process has successfully started. You can check the web console to see the progress (or list out your snapshots using the `aliyun` CLI).

## Known Issues

If you do not bind a custom domain name to your Function Compute function/service, then Function Compute will **force** the `Content-Disposition` header in the HTTP response to use `attachment` instead of `inline`. This means that the image file returned by Function Compute will be downloaded as a local file, rather than displayed in the browser.

Binding a domain name to function compute fixes this issue. See [here](https://www.alibabacloud.com/help/doc-detail/90722.htm) for instructions on how to do this.
