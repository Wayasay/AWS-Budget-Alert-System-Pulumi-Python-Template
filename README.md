# 💸 AWS Budget Alert System — Pulumi Python Template


## What does this do?

This template sets up an automatic email alert system that tells you when your AWS spending is getting too high — before you get a surprise bill.

Once deployed, you will receive an email when:
- You've spent **80%** of your monthly budget (early warning)
- You've spent **100%** of your monthly budget (you've hit the limit)
- AWS **predicts** you'll exceed your budget by month end (forward warning)

All of this is created with one command. No clicking around the AWS console.

---

## Before you start — what you need to install

You need 4 things before you can use this template. Follow each step in order.

---

### ✅ Step 1 — Create a free AWS account

If you don't have one already:

1. Go to [https://aws.amazon.com](https://aws.amazon.com)
2. Click **Create an AWS account**
3. Follow the sign-up steps (you'll need a credit card, but this template costs nothing to run — AWS Budgets and SNS email notifications are free tier)
4. Or if you have an account, just sign in..
---

### ✅ Step 2 — Create AWS Access Keys

AWS needs to know it's *you* making changes from your computer. Access keys are how it verifies that.

1. Log into the [AWS Console](https://console.aws.amazon.com)
2. Click your name in the top right → **Security credentials**
3. Scroll down to **Access keys** → click **Create access key**
4. Choose **Command Line Interface (CLI)** → tick the confirmation → click **Next**
5. Click **Create access key**
6. **Copy both keys and save them somewhere safe** — you won't be able to see the secret key again

> ⚠️ Never share these keys or commit them to GitHub. They give full access to your AWS account.

---

### ✅ Step 3 — Install and configure the AWS CLI

The AWS CLI is a tool that lets your computer talk to AWS. Pulumi uses it to authenticate.

**Install it:**

| System | Command |
|---|---|
| Mac | `brew install awscli` |
| Windows | Download from [aws.amazon.com/cli](https://aws.amazon.com/cli) |
| Linux | `sudo apt install awscli` or `pip install awscli` |

**Then configure it with your keys:**

```bash
aws configure
```

It will prompt you for 4 things:

```
AWS Access Key ID:     paste your Access Key ID here
AWS Secret Access Key: paste your Secret Access Key here
Default region name:   us-east-1
Default output format: just press Enter
```

**Test it worked:**

```bash
aws sts get-caller-identity
```

If you see your account ID and user name printed out, you're good to go.

---

### ✅ Step 4 — Install Python

Pulumi templates are written in Python. You need Python 3.8 or higher.

**Check if you already have it:**

```bash
python3 --version
```

If it says `Python 3.8` or higher, skip to Step 5.

**If not, install it:**

| System | How |
|---|---|
| Mac | `brew install python` |
| Windows | Download from [python.org](https://www.python.org/downloads/) |
| Linux | `sudo apt install python3` |

---

### ✅ Step 5 — Install the Pulumi CLI

Pulumi is the tool that reads the code in this template and creates the AWS resources.

**Install it:**

| System | Command |
|---|---|
| Mac | `brew install pulumi` |
| Windows | `winget install pulumi` |
| Linux | `curl -fsSL https://get.pulumi.com \| sh` |

**Then log in to Pulumi (free account):**

```bash
pulumi login
```

This opens your browser. Sign up for a free account at [app.pulumi.com](https://app.pulumi.com). Pulumi uses this to store a record of what infrastructure you've deployed (called "state"). The free tier is more than enough for personal use.

> 💡 Prefer not to use Pulumi Cloud? You can store state locally instead:
> `pulumi login --local`

---

## Now deploy the template

### 1. Clone this repo

```bash
git clone https://github.com/Wayasay/pulumi-budget-alert
cd pulumi-budget-alert
```

### 2. Install the Python dependencies

```bash
pip install -r requirements.txt
```

This installs the Pulumi AWS library that the code uses.

### 3. Create a new Pulumi stack

A "stack" is just a named instance of your infrastructure (like an environment).

```bash
pulumi stack init dev
```

### 4. Set your config values

Tell Pulumi your AWS region, monthly budget limit, and the email to send alerts to:

```bash
pulumi config set aws:region us-east-1
pulumi config set monthly_budget_usd 50
pulumi config set alert_email you@yourdomain.com
```

> Change `50` to whatever monthly limit you want in USD.
> Change `you@yourdomain.com` to your real email address.

### 5. Deploy

```bash
pulumi up
```

Pulumi will show you a preview of what it's about to create and ask you to confirm. Type `yes` and press Enter.

When it's done, you'll see output like this:

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

After deploying, AWS sends a confirmation email to the address you provided.

**You must open that email and click "Confirm subscription."**

Until you do this, the alerts are set up but your email won't receive them. This is an AWS security requirement — they don't send emails to addresses that haven't confirmed.

Check your spam folder if you don't see it within a few minutes.

---

## How it works under the hood

```
AWS Budget
  └── watches your monthly spend
        └── when it crosses a threshold →
              SNS Topic (notification channel)
                └── Email Subscription
                      └── your inbox
```

Three thresholds are set by default:
- **80% actual** — you've already spent 80% of your budget
- **100% actual** — you've spent your full budget
- **100% forecasted** — AWS predicts you'll exceed it by month end

---

## Tear it down

When you no longer need it:

```bash
pulumi destroy
```

This deletes all the resources from your AWS account. Your Pulumi stack record stays, but the AWS resources are gone.

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

**Add another email recipient:** Open `__main__.py` and duplicate the `TopicSubscription` block with a different email address.

**Add more alert thresholds:** Duplicate one of the `BudgetNotificationArgs` blocks in `__main__.py` and change the `threshold` value.

---

## What does each file do?

| File | Purpose |
|---|---|
| `__main__.py` | The infrastructure code — this is what Pulumi deploys |
| `Pulumi.yaml` | The project config — tells Pulumi the project name and language |
| `requirements.txt` | The Python libraries this project depends on |

---

## Common errors and fixes

**`No credentials found`**
You haven't configured the AWS CLI yet. Go back to Step 3 above and run `aws configure`.

**`Missing required config: monthly_budget_usd`**
You haven't run the `pulumi config set` commands. Go back to the Deploy section above.

**`Error: ACCOUNT_CANNOT_CREATE_BUDGET`**
Your AWS account needs billing access enabled. Go to AWS Console → Billing → Billing preferences → tick "Receive Billing Alerts".

**Alerts not arriving in your inbox**
You haven't confirmed the subscription email. Check your spam folder and click the confirmation link.

---

Never get a surprise AWS bill again. This template spins up a monthly budget with email alerts at **80%**, **100% actual spend**, and **100% forecasted spend** — all version-controlled and deployable in one command.

---

## What gets created

| Resource | Purpose |
|---|---|
| `aws.sns.Topic` | Notification broadcast channel |
| `aws.sns.TopicSubscription` | Wires your email to the channel |
| `aws.budgets.Budget` | Tracks your monthly AWS spend |
| Budget Notifications (×3) | Fires at 80%, 100% actual, 100% forecasted |

---

## Prerequisites

- [Pulumi CLI](https://www.pulumi.com/docs/install/) installed
- [Python 3.8+](https://www.python.org/downloads/)
- AWS credentials configured (`aws configure` or environment variables)

---

## Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/Wayasay/pulumi-budget-alert
cd pulumi-budget-alert

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your config
pulumi config set aws:region us-east-1
pulumi config set monthly_budget_usd 50
pulumi config set alert_email you@yourdomain.com

# 4. Deploy
pulumi up
```

**⚠️ Important:** After deploying, check your inbox for a confirmation email from AWS SNS. You must click **"Confirm subscription"** before alerts will fire.

---

## Tear it down

```bash
pulumi destroy
```

---

## Customise it

- Change `monthly_budget_usd` to any number (e.g. `100`, `200`)
- Add extra notification thresholds by duplicating a `BudgetNotificationArgs` block
- Subscribe multiple emails by adding more `aws.sns.TopicSubscription` resources

---
