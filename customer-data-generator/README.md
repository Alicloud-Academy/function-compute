# MySQL DB Data Generator - Function Compute Example

- Status: **OK**
- Notes: Code tested and working as of 2021-12-10 (YYYY-MM-DD)

## What Does The Code Do?

This code generates fake users, products, and orders, and inserts them into a MySQL database.

The code is designed to work with any MySQL database, but is especially well suited to talking to RDS MySQL databases within a VPC (this is the use-case it is designed around).

The code consists of three Function Compute functions, `user_generator`, `product_generator`, and `order_generator`, and a configuration file - `s.yaml` - which [Serverless Devs](https://www.alibabacloud.com/help/doc-detail/195473.htm) (Alibaba Cloud's serverless development toolkit) uses to build and deploy those 3 functions.

## Setting Up Your Database

The code expects to find `users`, `products`, and `orders` tables in your database. You can create them using the following DDL statements:

```SQL
CREATE TABLE `orders` (
    `order_id` bigint NOT NULL AUTO_INCREMENT,
    `year` varchar(32) NULL,
    `month` varchar(32) NULL,
    `product_code` bigint NULL,
    `quantity` bigint NULL,
    `user_id` bigint NULL,
    PRIMARY KEY (`order_id`)
) ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8;

CREATE TABLE `products` (
    `product_id` bigint NOT NULL AUTO_INCREMENT,
    `product_name` varchar(32) NULL,
    `price` float NULL,
    PRIMARY KEY (`product_id`)
) ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8;

CREATE TABLE `users` (
    `user_id` bigint NOT NULL AUTO_INCREMENT,
    `name` varchar(32) NULL,
    `age` bigint NULL,
    `sex` varchar(32) NULL,
    `country` varchar(32) NULL,
    `country_code` varchar(32) NULL,
    PRIMARY KEY (`user_id`)
) ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8;
```

Make sure these tables exist before you attempt to build, deploy, or call the Function Compute code contained in this repository.

You also need to **make sure that Function Compute can access your database**. If your database is an RDS MySQL database, you need to **update your whitelist settings** to allow traffic from within the VPC your MySQL instance is attached to. For instance, if the CIDR block of your VPC is `192.168.0.0/16`, you would add that to your RDS instance's IP address whitelist. 

## Setting Up Your Environment 

To build the code, you'll need to have Docker installed. To deploy it, you'll need Serverless Devs. Instructions are here:

- Install [Docker](https://www.docker.com/get-started)
- Install [Serverless Devs](https://www.alibabacloud.com/help/doc-detail/195474.htm)

If you have never used Serverless Devs before, you'll need to set it up first. To call Serverless Devs from the command line, just use `s`. That's right...the name of the Serverless Devs CLI tool is just the letter "s"! So to configure Serverless Devs, you would run the following from a terminal window:

```
s config add
```

You'll need to enter your Alibaba Cloud account ID, as well as valid Access Key and Access Key secret. We recommend you setup a RAM user and attach an Access Key to that user, rather than directly creating an Access Key under your primary (root) account. 

## Getting The Code Ready

If you look inside each of the three `index.py` files that correspond to the user_generator, order_generator, and product_generator functions, you'll see a section like this near the top:

```python
config = {
  'user': 'db_username',
  'password': 'db_password',
  'host': 'db_endpoint',
  'database': 'db_name',
  'raise_on_warnings': True
}
```

**Make sure you modify this section in all 3 `index.py` files** to match your database name, database username, database password, and database connection string (host). Note, you do **not** need to put "jdbc://" or any other designator at the beginning of your database address. For example, if your database is an RDS MySQL database on Alibaba Cloud, your `host` value might look something like this:

```
  'host': 'rm-t4n5tqw3w42p0246n.mysql.singapore.rds.aliyuncs.com',
```

That's it. No "jdbc://" or port number needed. 

It goes without saying that **you really don't want to do things this way in production**. Rather, you would store your credentials somewhere else (say - as Function Compute environment variables) and pass them in at run time. 

## Updating The `s.yaml` File

You'll also need to make some changes to `s.yaml`. Specifically, you need to update several values in the `vars` section at the top of that file:

```
vars:
  region: your_region
  ecomm_service:
    name: ecomm_service
    description: E-Commerce data generator service
    role: acs:ram::your_account_id:role/fc-role-name
    internetAccess: false
    vpcConfig:
      vpcId: your_vpc
      vswitchIds:
        - your_vswitch
      securityGroupId: your_sg
    tracingConfig: Disable
```

Any line with `your` in it needs to be modified. Specifically, you need to change these values:

- `region:` 

Set this to the region where you want to deploy your Function Compute code (say, ap-southeast-1, for Singapore). Ideally, this should be the same region where your database is deployed.

- `role:` 

Set this to a valid RAM role ARN that Function Compute can use to update VPC settings (needed to allow Function Compute to talk to RDS MySQL databases over the VPC network).

- `vpcID:` 

Set this to the VPC ID of the VPC that contains your RDS MySQL database.

- `vswitchIds:` 

Add at least one valid VSwitch ID to this section, corresponding to one of the VSwitches in your VPC. It doesn't matter whether you choose the subnet your RDS MySQL database is attached to, or some other subnet in the VPC. By default, VSwitches can communicate with each other so long as they are in the same VPC. 

- `securityGroupId:` 

Set this to a valid Security Group ID associated with your VPC. In our case, it doesn't matter very much which Security Group: RDS MySQL is going to allow or deny access to the database via an IP address whitelist rather than by Security Group ID. 

### The tricky part: RAM Role access

You'll also notice this line:

```
role: acs:ram::your_account_id:role/fc-role-name
```

You need to replace `your_account_id` with your own Alibaba Cloud account ID number, and `fc-role-name` with a RAM role that Function Compute can assume to manipulate VPC network settings.

If you've used Function Compute inside a VPC before, you may already have a role under your account called `fc-default-role`, which you can reuse here.

If not, you'll need to create that role yourself. The role should be a "Normal Service Role" with a trust policy that allows Function Compute to assume the role, and it should be bound to the `AliyunECSNetworkInterfaceManagementAccess` system policy.

You can find step-by-step setup instructions in [this blog post](https://www.alibabacloud.com/blog/598341). Specifically, look at the paragraphs near the end of the section **Modifying The Code**. 

## Build And Deploy The Code

You can now build the code locally by simply running:

```
s build
```

From the directory containing the `s.yaml` file. 

Once the build completes, you can deploy the code to Alibaba Cloud with:

```
s deploy
```

During the deploy process, you might be asked whether or not to allow Serverless Devs (the `s` tool) to set certain environment variables associated with building the Function Compute code. Choose `yes`. 

Once the functions are deployed, Serverless Devs will output information about your functions and their triggers, as well as three function URLs that look like this one (yours will of course be a little different):

```
https://1846872507351065.ap-southeast-1.fc.aliyuncs.com/2016-08-15/proxy/ecomm_service/user_generator/
```

```
https://1846872507351065.ap-southeast-1.fc.aliyuncs.com/2016-08-15/proxy/ecomm_service/product_generator/
```

```
https://1846872507351065.ap-southeast-1.fc.aliyuncs.com/2016-08-15/proxy/ecomm_service/order_generator/
```

You can call these with a command like `wget` or `curl` to invoke them, or simply paste them into a web browser like Chrome.

Some of them have **mandatory URL parameters**. To learn what those are and how to set them, look at the comments in each `index.py` file. 

## Cleaning Up 

You can use the `s remove` command to un-deploy your Function Compute code. 

This doesn't always work, so you *may* need to remove things manually sometimes. If you *do* have to delete your Function Compute environment manually, you can do so from the Alibaba Cloud web console. Just make sure to delete things in the following order

1. Triggers
2. Functions
3. Services

## Next Steps

If you want a step-by-step tutorial that walks you through the whole process of setting up the environment and testing it out, you can check out [this blog post](https://www.alibabacloud.com/blog/598341).

## Known Issues

If you do not bind a custom domain name to your Function Compute function/service, then Function Compute will **force** the `Content-Disposition` header in the HTTP response to use `attachment` instead of `inline`. This means that the image file returned by Function Compute will be downloaded as a local file, rather than displayed in the browser.

Binding a domain name to function compute fixes this issue. See [here](https://www.alibabacloud.com/help/doc-detail/90722.htm) for instructions on how to do this.
