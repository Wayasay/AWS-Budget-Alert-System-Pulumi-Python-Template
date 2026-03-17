# 💸 AWS Budget Alert System — Pulumi Python Template

## What does this do?

This template sets up an automatic email alert system that tells you when your AWS spending is getting too high — before you get a surprise bill.

Once deployed, you will receive an email when:
- You've spent **80%** of your monthly budget (early warning — time to investigate)
- You've spent **100%** of your monthly budget (you've hit the limit)
- AWS **predicts** you'll exceed your budget before the month ends (forward warning)

All of this is created with one command. No clicking around the AWS console.

---

## Before you start — what you need to install

You need 5 things before you can use this template. **The order matters** — each step builds on the last. If you skip ahead and run `pulumi up` before completing the steps, you will get errors.

Here is why the order matters:

```
aws configure    →  you put a key under the doormat
pulumi login     →  you register with the locksmith
pulumi up        →  the locksmith picks up the key and opens the door
```

Pulumi doesn't have its own AWS login. It borrows the credentials that `aws configure` already stored on your machine. So AWS access has to be set up first — Pulumi picks it up automatically when you deploy. You only have to do all of this once. After that, every future template you use will just work.

---

### ✅ Step 1 — Create a free AWS account

If you don't have one already:

1. Go to [https://aws.amazon.com](https://aws.amazon.com)
2. Click **Create an AWS account**
3. Follow the sign-up steps (you'll need a credit card, but this template costs nothing to run — AWS Budgets and SNS email alerts are both free tier)
4. Or sign in if you already have one

---

### ✅ Step 2 — Create AWS Access Keys

AWS needs to verify it's you making changes from your computer. Access keys are how it does that — think of them as a username and password specifically for your terminal.

1. Log into the [AWS Console](https://console.aws.amazon.com)
2. Click your name in the top right → **Security credentials**
3. Scroll down to **Access keys** → click **Create access key**
4. Choose **Command Line Interface (CLI)** → tick the confirmation box → click **Next**
5. Click **Create access key**
6. **Copy both keys and save them somewhere safe** — you won't be able to see the Secret Access Key again after closing this screen

> ⚠️ Never share these keys or commit them to GitHub. Anyone who has them has full access to your AWS account.

---

### ✅ Step 3 — Install and configure the AWS CLI

The AWS CLI is a tool that lets your computer communicate with AWS. This is the step where you hand your access keys to your machine — and where Pulumi will quietly pick them up later when it needs to deploy.

**Install it:**

| System | Command |
|---|---|
| Mac | `brew install awscli` |
| Windows | Download from [aws.amazon.com/cli](https://aws.amazon.com/cli) |
| Linux | `sudo apt install awscli` or `pip install awscli` |

**Configure it with your access keys:**

```bash
aws configure
```

It will prompt you for 4 things — enter them one at a time:

```
AWS Access Key ID:     paste your Access Key ID here
AWS Secret Access Key: paste your Secret Access Key here
Default region name:   us-east-1
Default output format: just press Enter to skip
```

When you run this, the AWS CLI writes your credentials to a file at `~/.aws/credentials` on your machine. This file stays there permanently — you only need to do this once. Every time you run `pulumi up` in the future, Pulumi reads your credentials from this file automatically. You won't be asked to log into AWS again.

**Verify it worked:**

```bash
aws sts get-caller-identity
```

If you see your AWS account ID and username printed in the terminal, your credentials are working correctly and you're ready to move on.

---

### ✅ Step 4 — Install Python

The infrastructure code in this template is written in Python. You need Python 3.8 or higher.

**Check if you already have it:**

```bash
python3 --version
```

If it shows `Python 3.8` or higher, skip straight to Step 5.

**If not, install it:**

| System | How |
|---|---|
| Mac | `brew install python` |
| Windows | Download from [python.org](https://www.python.org/downloads/) |
| Linux | `sudo apt install python3` |

---

### ✅ Step 5 — Install the Pulumi CLI and log in

Pulumi is the tool that reads the code in this template and creates the real AWS resources. It also needs to store a record of what it has deployed — this is called "state" — so it knows what exists and what needs to change next time you run it.

**Install it:**

| System | Command |
|---|---|
| Mac | `brew install pulumi` |
| Windows | `winget install pulumi` |
| Linux | `curl -fsSL https://get.pulumi.com \| sh` |

**Log in to Pulumi Cloud (free):**

```bash
pulumi login
```

This opens your browser and asks you to create a free account at [app.pulumi.com](https://app.pulumi.com). Pulumi uses this account to store your stack state remotely — a record of every resource it has deployed on your behalf.

This is a separate login from AWS. Think of it this way:
- **AWS login** (`aws configure`) = permission to create resources in your AWS account
- **Pulumi login** (`pulumi login`) = where Pulumi keeps its own notes about what it built

You need both.

> 💡 Prefer not to use Pulumi Cloud? You can store state on your local machine instead:
> `pulumi login --local`

---

## Deploy the template

Once all 5 setup steps are done, you're ready. Here's what happens from clone to deployed:

### 1. Clone this repo

```bash
git clone https://github.com/Wayasay/pulumi-budget-alert
cd pulumi-budget-alert
```

### 2. Install the Python dependencies

```bash
pip install -r requirements.txt
```

This installs the Pulumi AWS library that the code imports. Without this step, Python won't recognise the `pulumi_aws` module in `__main__.py`.

### 3. Create a Pulumi stack

```bash
pulumi stack init dev
```

A stack is a named instance of your infrastructure — think of it as an environment label. Calling it `dev` is convention. This command also creates a file called `Pulumi.dev.yaml` in your project folder, which is where your config values will be stored in the next step.

### 4. Set your config values

```bash
pulumi config set aws:region us-east-1
pulumi config set monthly_budget_usd 50
pulumi config set alert_email you@yourdomain.com
```

Replace `50` with your monthly budget limit in USD, and `you@yourdomain.com` with your real email address.

**You do not need to edit `__main__.py` at all.** These three commands are the only customisation required. Pulumi writes your values into `Pulumi.dev.yaml` automatically — the file is created for you and looks like this:

```yaml
config:
  aws:region: us-east-1
  pulumi-budget-alert:alert_email: you@yourdomain.com
  pulumi-budget-alert:monthly_budget_usd: "50"
```

Your project folder will now contain:

```
pulumi-budget-alert/
  __main__.py        ← infrastructure code (you don't touch this)
  Pulumi.yaml        ← project name and language
  Pulumi.dev.yaml    ← your config values (auto-created by Pulumi)
  requirements.txt   ← Python dependencies
```

`Pulumi.dev.yaml` is safe to commit to GitHub. If you ever store a sensitive value using `pulumi config set --secret`, Pulumi encrypts it before writing it to this file so the raw value is never exposed.

### 5. Deploy

```bash
pulumi up
```

This is the moment everything connects:

1. Pulumi reads `__main__.py` to know what to build
2. It reads `Pulumi.dev.yaml` to get your config values
3. It reads `~/.aws/credentials` to authenticate with AWS
4. It calls AWS and creates the resources in your account
5. It saves a record of what was built to your Pulumi Cloud state

Pulumi will show you a preview first and ask you to confirm. Type `yes` and press Enter.

When it finishes, you'll see output like this:

```
Outputs:
  alert_email:    you@yourdomain.com
  budget_name:    pulumi-budget-alert-monthly-budget-xxxx
  monthly_limit:  $50 USD
  next_step:      ⚠️ Check your inbox and click 'Confirm subscription' to activate your alerts.
  sns_topic_arn:  arn:aws:sns:us-east-1:123456789:pulumi-budget-alert-billing-alerts
```

---

## ⚠️ Critical last step — confirm your email

After deploying, AWS will send a confirmation email to the address you provided.

**You must open that email and click "Confirm subscription."**

Until you do this, everything is set up correctly but your inbox will not receive the alerts. AWS requires this as a security measure — they won't send emails to addresses that haven't explicitly opted in.

If you don't see the email within a few minutes, check your spam folder.

---

## How it works under the hood

```
AWS Budget
  └── watches your monthly spend in real time
        └── when spend crosses a threshold →
              SNS Topic (a notification broadcast channel)
                └── Email Subscription
                      └── your inbox
```

Three alert thresholds are configured by default:
- **80% actual** — you've already spent 80% of your budget. Still time to act.
- **100% actual** — you've spent your full budget. Check what's running.
- **100% forecasted** — AWS projects you'll exceed your limit before month end, even if you haven't yet.

---

## What does each file do?

| File | Purpose |
|---|---|
| `__main__.py` | The infrastructure code — this is what Pulumi reads and deploys |
| `Pulumi.yaml` | The project definition — tells Pulumi the project name and language |
| `Pulumi.dev.yaml` | Your config values — auto-created when you run `pulumi config set` |
| `requirements.txt` | The Python libraries this project depends on |

---

## Tear it down

When you no longer need it:

```bash
pulumi destroy
```

This removes all the AWS resources from your account. Your `Pulumi.dev.yaml` and stack record stay, but nothing is running in AWS.

---

## Customise it

**Change your budget limit:**
```bash
pulumi config set monthly_budget_usd 100
pulumi up
```

**Change your alert email:**
```bash
pulumi config set alert_email newaddress@yourdomain.com
pulumi up
```

**Add a second email recipient:** Open `__main__.py` and duplicate the `aws.sns.TopicSubscription` block with a different email address.

**Add more alert thresholds:** Duplicate one of the `BudgetNotificationArgs` blocks in `__main__.py` and change the `threshold` value to whatever percentage you want.

---

## Common errors and fixes

**`No credentials found`**
You haven't configured the AWS CLI yet. Go back to Step 3 and run `aws configure`.

**`Missing required config: monthly_budget_usd`**
You haven't run the `pulumi config set` commands yet. Go back to the Deploy section and set all three values.

**`Error: ACCOUNT_CANNOT_CREATE_BUDGET`**
Your AWS account needs billing access enabled. Go to AWS Console → Billing → Billing preferences → tick **Receive Billing Alerts**.

**`pulumi up` fails with an authentication error**
Your Pulumi session may have expired. Run `pulumi login` again to refresh it.

**Alerts not arriving in your inbox**
You haven't confirmed the subscription email. Check your spam folder and click the confirmation link.