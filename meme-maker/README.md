# Meme Maker - Function Compute Example

- Status: **OK**
- Notes: Code tested and working as of 2020-06-11 (YYYY-MM-DD)

## What

The function compute code in the `fc-function` folder sets up a "meme service", and creates a "meme function" written in Python 3, with an HTTP trigger.

Once the service is up and running, you can call the service (using the Function Compute URL or a custom domain bound to Function Compute). By including the URL parameters `imgUrl`, `topText`, and `bottomText`, you can direct this FC function to caption an arbitrary image from anywhere on the Internet and return the result to you as a JPEG image. For example:

![A Very Grumpy Cat...](meme.jpeg)

## How

### But first...

Before you get started, you need to install Docker as well as the Alibaba Cloud function compute command line tool, `fun`. 

- Information on installing Docker is [here](https://docs.docker.com/get-docker/)
- Installation instructions for `fun` are [here](https://www.alibabacloud.com/help/doc-detail/161136.htm)

Note that the `fun` command line tool is **distributed using NPM** so you'll need to have node installed in order to install fun. If you are on a Mac, you might want to consider installing node through [Homebrew](https://brew.sh/), a handy Mac package manager.

After you install `fun` you need to run `fun configure` and enter your Account ID, Access Key, Access Key Secret, and the default Alibaba Cloud region (this is where `fun` will deploy functions when you run `fun deploy`). Details on configuring `fun` can be found on [this page](https://www.alibabacloud.com/help/doc-detail/146702.htm). 

### Ok, let's really do this

From the `fc-function` directory, you'll need to run `fun build` which will build your function and pull in any external dependencies (from apt or pip) defined in `fun.yml`. Finally, run `fun deploy` to deploy your code onto Alibaba Cloud. `fun deploy` will look at the contents of `template.yml` to determine how your function (and the service containing it) should be named, as well as any triggers that should be configured (in this case, an HTTP trigger). 

So remember, the steps to deploy are:

1. `fun build`
2. `fun deploy`

That's it! See the section below to learn how to generate valid URI strings to actually call the new FC function via curl or your favorite web browser.

### Testing it out

One of the outputs returned by `fun deploy` is the URL endpoint of our new Function Compute function. But how can we generate a URL with the correct parameters `imgUrl`, `topText`, and `bottomText`? And how will we handle encoding special characters? 

Enter `genUrl.py`. This handy utility program can be found in the `utilities` directory. It takes as input your function's URL, the URL of the image you want to meme-ify, and your top and bottom text. It also accepts an optional *custom domain* parameter, in case you've bound a custom domain to your function, such as `meme.functionsarecool.com`. 

Here's an example of `genUrl.py` in action:

```
$> python3 genURL.py
Could not find local .memeconfig file, creating one...
(REQUIRED) Enter FC URL (previous: ): https://5483593200991628.ap-southeast-1.fc.aliyuncs.com/2016-08-15/proxy/meme-srv/meme-fun/
(REQUIRED) Enter image URL (previous: ): https://imagez.tmz.com/image/53/4by3/2019/10/09/5326dbf3d45445c3b11d33994cc4728d_md.jpg
(OPTIONAL) Enter FC custom domain name (previous: ): memes.functiontime.xyz
(OPTIONAL) Enter meme top text (previous: ): I had fun once
(OPTIONAL Enter meme bottom text (previous: ): It was awful

**********
http://memes.functiontime.xyz/2016-08-15/proxy/meme-srv/meme-fun/?imgUrl=https%3A%2F%2Fimagez.tmz.com%2Fimage%2F53%2F4by3%2F2019%2F10%2F09%2F5326dbf3d45445c3b11d33994cc4728d_md.jpg&topText=I+had+fun+once&bottomText=It+was+awful
**********
```

To save you the trouble of entering the same things over and over again, `genUrl.py` saves the parameters you enter into a local `.memeconfig` file. The next time you run `genUrl.py` it will pull your last-used parameters from there. This saves you some typing, if you only want to change one field (such as the image url or meme text).

## Other Notes

If you are just curious about how Python's PIL was used to make memes, and aren't interested in reading  through all the URL parsing code in index.py (our Function Compute function code), take a look at `utilities/imageFetcher.py`, which contains just the meme generation code. This Python script takes a URL, top text, and bottom text as input. It uses Python `requests` to fetch the photo, and PIL to add text to the image and save it to disk. It saves both the original photo fetched by `requests`, as well as the newly edited photo, which goes in a file called `out.jpg`. Note the extension could vary, it depends on the extension used by the original image. 

## Issues

If you do not bind a custom domain name to your Function Compute function, then the Function Compute service will **force** the `Content-Disposition` header in the HTTP response to use `attachment` instead of `inline`. This means that the image file returned by Function Compute will be downloaded as a local file, rather than displayed in the browser.

Binding a domain name to function compute fixes this issue. See [here](https://www.alibabacloud.com/help/doc-detail/90722.htm) for instructions on how to do this.

Don't worry: your function still works just fine even without a custom domain, but the file downloaded by your browser may be missing its extension (such as `.jpg` or `.png`), and you'll have to rename the file in order to open it. *We recommend you bind a custom domain name if possible*.

## Credits

My Python 3 meme-maker code was inspired by [this awesome blog post](https://blog.lipsumarium.com/caption-memes-in-python/). The font oswald_bold.ttf I use to caption memes comes from [here](https://fonts.google.com/specimen/Oswald).