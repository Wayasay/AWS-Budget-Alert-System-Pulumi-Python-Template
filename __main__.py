"""
WHAT THIS FILE DOES:
This file is your infrastructure. When you run `pulumi up`,
Pulumi reads this file and creates real AWS resources in your account.
Think of it like a recipe — Pulumi is the chef that follows it.

WHAT GETS CREATED:
  1. An SNS Topic       — a notification channel in AWS
  2. An Email Sub       — connects your inbox to that channel
  3. An AWS Budget      — watches your monthly spend
  4. 3 Alert Rules      — fires when you hit 80%, 100%, or are forecasted to exceed

BEFORE YOU RUN THIS:
  See the README.md for the full setup guide (AWS account, CLI, Pulumi login).
  Then run these 4 commands in your terminal:

    pulumi config set aws:region us-east-1
    pulumi config set monthly_budget_usd 50
    pulumi config set alert_email you@yourdomain.com
    pulumi up
"""

# ── Imports 
# These two lines load the Pulumi libraries.
# `pulumi`     = the core tool that manages your infrastructure
# `pulumi_aws` = the AWS plugin that lets Pulumi talk to AWS services
import pulumi
import pulumi_aws as aws


# ── Config 
# This reads the values you set via `pulumi config set ...` in your terminal.
# It means you never have to hardcode sensitive values like emails or amounts
# directly into this file — they stay separate and safe.
config        = pulumi.Config()
monthly_limit = config.require("monthly_budget_usd")  # e.g. "50" means $50/month
alert_email   = config.require("alert_email")          # the inbox that receives alerts
project_name  = pulumi.get_project()                   # the name from your Pulumi.yaml file


# ── Step 1: Create an SNS Topic
# SNS stands for Simple Notification Service.
# Think of it like a group chat in AWS — you create the chat first,
# then invite people (subscribers) to join it.
# When AWS Budget wants to send an alert, it posts a message to this "chat".
# Everyone subscribed to it will receive that message.
#
# Right now it's an empty channel — no one is listening yet.
# We connect the email in the next step.
billing_topic = aws.sns.Topic(
    f"{project_name}-billing-alerts",   # the name of the topic inside AWS
    display_name="AWS Budget Alerts",   # a human-readable label shown in emails
    tags={
        "managed-by": "pulumi",         # tags help you track what created this resource
        "project": project_name,
    },
)


# ── Step 2: Subscribe an Email to the Topic 
# Now we add your email address as a subscriber to the SNS topic above.
# This is like joining that group chat — you'll receive every message posted to it.
#
# `billing_topic.arn` is the unique ID of the topic we just created above.
# ARN stands for Amazon Resource Name — every AWS resource gets one automatically.
# Pulumi passes it here so AWS knows which topic to subscribe you to.
#
# ⚠️  IMPORTANT: After `pulumi up`, AWS will send you a confirmation email.
#     You MUST click "Confirm subscription" in that email.
#     Until you do, alerts will NOT be delivered to your inbox.
email_subscription = aws.sns.TopicSubscription(
    f"{project_name}-email-sub",
    topic=billing_topic.arn,    # connect this subscription to the topic above
    protocol="email",           # the delivery method — we want email
    endpoint=alert_email,       # the email address to deliver to
)


# ── Step 3: Create the Budget with Alert Rules 
# AWS Budgets is a service that watches your account spending.
# You tell it your monthly limit, and it checks your spend in real time.
# When your spend crosses a threshold, it fires a notification to the SNS topic.
# The SNS topic then delivers it to your email.
#
# We set up 3 alerts so you get a heads-up before things go wrong:
#   Alert 1 → 80% of your actual spend   (early warning — time to investigate)
#   Alert 2 → 100% of your actual spend  (you've hit the limit)
#   Alert 3 → 100% forecasted spend      (AWS predicts you'll exceed it this month)
monthly_budget = aws.budgets.Budget(
    f"{project_name}-monthly-budget",
    budget_type="COST",             # we're tracking cost (not usage or coverage)
    limit_amount=monthly_limit,     # the monthly limit you set in config
    limit_unit="USD",               # currency
    time_unit="MONTHLY",            # reset the budget tracker every month

    notifications=[

        # ── Alert 1: You've spent 80% of your budget 
        # This is your early warning. You still have 20% left to act.
        # "ACTUAL" means it's based on real spend that has already happened.
        aws.budgets.BudgetNotificationArgs(
            comparison_operator="GREATER_THAN",         # trigger when spend goes above...
            notification_type="ACTUAL",                 # ...your real (not predicted) spend
            threshold=80,                               # ...80%
            threshold_type="PERCENTAGE",                # threshold is a % of your limit
            subscriber_sns_topic_arns=[billing_topic.arn],  # send the alert to our SNS topic
        ),

        # ── Alert 2: You've spent 100% of your budget 
        # You've hit your limit. Time to check what's running.
        aws.budgets.BudgetNotificationArgs(
            comparison_operator="GREATER_THAN",
            notification_type="ACTUAL",                 # real spend
            threshold=100,                              # 100% of your limit
            threshold_type="PERCENTAGE",
            subscriber_sns_topic_arns=[billing_topic.arn],
        ),

        # ── Alert 3: AWS predicts you'll exceed your budget 
        # "FORECASTED" means AWS is looking at your spend rate and projecting
        # where you'll land by the end of the month — even if you haven't hit
        # the limit yet. This gives you time to course-correct early.
        aws.budgets.BudgetNotificationArgs(
            comparison_operator="GREATER_THAN",
            notification_type="FORECASTED",             # based on predicted spend
            threshold=100,
            threshold_type="PERCENTAGE",
            subscriber_sns_topic_arns=[billing_topic.arn],
        ),
    ],
    tags={
        "managed-by": "pulumi",
        "project": project_name,
    },
)

# ── Outputs 
# These lines print useful information to your terminal after `pulumi up` finishes.
# They confirm what was created and remind you of the one manual step required.
pulumi.export("sns_topic_arn",  billing_topic.arn)
pulumi.export("budget_name",    monthly_budget.name)
pulumi.export("alert_email",    alert_email)
pulumi.export("monthly_limit",  f"${monthly_limit} USD")
pulumi.export("next_step",      "⚠️  Check your inbox and click 'Confirm subscription' to activate your alerts.")
